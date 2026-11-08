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
