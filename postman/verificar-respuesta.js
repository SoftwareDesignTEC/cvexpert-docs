const expected = CASO;
let passed = true;

function verify(name, assertResponse) {
    pm.test(name, () => {
        try {
            assertResponse();
        } catch (error) {
            passed = false;
            throw error;
        }
    });
}

verify("Estado HTTP esperado", () => pm.expect(pm.response.code).to.be.oneOf(expected.status));

if (passed && !expected.statusOnly) {
    if (pm.response.code === 204) {
        verify("Respuesta sin cuerpo", () => pm.expect(pm.response.text()).to.equal(""));
    } else if (expected.schemas[pm.response.code]) {
        verify("Tipo de respuesta JSON", () => {
            pm.expect(pm.response.headers.get("Content-Type")).to.match(/^application\/json(?:\s*;|$)/i);
        });
        verify("Estructura según el contrato", () => {
            pm.response.to.have.jsonSchema(expected.schemas[pm.response.code]);
        });
        if (passed) {
            const data = pm.response.json();
            if (expected.refresh) {
                verify("Contadores de recarga de ofertas", () => {
                    for (const field of ["created", "updated", "failedQueries"]) {
                        pm.expect(data[field]).to.be.a("number");
                        pm.expect(Number.isSafeInteger(data[field]) && data[field] >= 0).to.equal(true);
                    }
                });
                if (passed) pm.variables.set("runJobRefreshComplete", "true");
            }
            for (const field of expected.nonempty) {
                verify("Contenido no vacío de " + field, () => pm.expect(data[field]).to.be.a("string").and.not.empty);
            }
            if (expected.photo) {
                verify("URL pública HTTPS de fotografía", () => pm.expect(data.url).to.match(/^https:\/\//));
            }
            if (expected.gap) {
                verify("Resultado asociado a la proyección sintética", () => {
                    pm.expect(data.cvId).to.equal("cv:test");
                    pm.expect(data.dataSource).to.equal("client_request");
                    pm.expect(data.results).to.have.lengthOf(1);
                    pm.expect(data.results[0].jobId).to.equal("job:test");
                });
                const result = data.results[0];
                const empty = expected.gap.startsWith("empty");
                verify("Cobertura documental y ausencias", () => {
                    pm.expect(result.status).to.equal(empty ? "insufficient_information" : "partial");
                    pm.expect(result.documentedCoveragePercent).to.equal(empty ? null : 66.67);
                    pm.expect(result.notDocumentedSkills).to.eql(empty ? [] : ["Docker"]);
                });
                if (expected.gap === "levels") {
                    verify("Niveles explícitos separados de cobertura", () => {
                        pm.expect(result.levelAnalysis.scale).to.equal("cv-skill-v1");
                        pm.expect(result.levelAnalysis.belowRequiredCount).to.equal(1);
                        pm.expect(result.levelAnalysis.meetsRequiredCount).to.equal(1);
                        pm.expect(result.skillLevelAssessments[0].requiredLevel).to.equal("advanced");
                        pm.expect(result.skillLevelAssessments[0].deficitSteps).to.equal(1);
                    });
                }
                if (expected.gap === "names") {
                    verify("Respuesta compatible sin texto", () => {
                        pm.expect(result).to.not.have.property("levelAnalysis");
                        pm.expect(result).to.not.have.property("skillLevelAssessments");
                    });
                }
                if (expected.gap === "courses" || expected.gap === "empty_courses") {
                    verify("Recomendaciones por ausencia y catálogo", () => {
                        pm.expect(result.recommendations).to.have.lengthOf(empty ? 0 : 1);
                        for (const recommendation of result.recommendations) {
                            pm.expect(recommendation.skillName).to.equal("Docker");
                            pm.expect(recommendation.courses.length).to.be.at.most(5);
                            const ids = recommendation.courses.map(course => course.id);
                            pm.expect(new Set(ids).size).to.equal(ids.length);
                            if (recommendation.catalogMatch !== "matched") pm.expect(ids).to.have.lengthOf(0);
                        }
                    });
                }
            }
            for (const [key, value] of Object.entries(expected.checks)) {
                const wanted = typeof value === "string" ? pm.variables.replaceIn(value) : value;
                verify("Valor esperado de " + key, () => pm.expect(data[key]).to.eql(wanted));
            }
            if (data && Array.isArray(data.items) && Number.isInteger(data.pageSize)) {
                verify("La cantidad de elementos respeta pageSize", () => {
                    pm.expect(data.items.length).to.be.at.most(data.pageSize);
                });
            }
            if (expected.template) {
                verify("Metadatos de edición de plantilla", () => {
                    for (const template of Array.isArray(data) ? data : [data]) {
                        if (template.updatedAt === 0 && !expected.updatedTemplate) {
                            pm.expect(template).to.not.have.property("updatedBy");
                        } else {
                            pm.expect(template.updatedAt).to.be.above(0);
                            pm.expect(template.updatedBy).to.be.a("string").and.not.empty;
                        }
                    }
                });
            }
            if (expected.captureFirst) {
                verify("El catálogo aporta una plantilla para el flujo", () => {
                    pm.expect(data.items[0]?.id).to.be.a("string").and.not.empty;
                });
                if (passed) pm.variables.set(expected.captureFirst, data.items[0].id);
            }
            for (const [field, variable] of Object.entries(expected.capture)) {
                verify("Identificador de flujo: " + field, () => {
                    pm.expect(data[field]).to.be.a("string").and.not.empty;
                });
                if (passed) pm.variables.set(variable, data[field]);
            }
        }
    }
}
