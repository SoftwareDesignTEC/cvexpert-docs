#!/usr/bin/env node
// Ejecuta Newman y presenta resultados sin imprimir URLs, cabeceras ni cuerpos.
const { readFileSync } = require("node:fs");
const { join } = require("node:path");
const { Script } = require("node:vm");
const root = join(__dirname, "..");
const example = join(root, "postman", "apim.postman_environment.json");
const collection = JSON.parse(readFileSync(join(root, "postman", "cvexpert.postman_collection.json"), "utf8"));
const groups = collection.item.map(folder => folder.name);
const [input, ...folders] = process.argv.slice(2);

if (input === "--sintaxis") {
    for (const item of [collection, ...collection.item.flatMap(folder => folder.item)]) {
        for (const event of item.event) {
            new Script(event.script.exec.join("\n"), { filename: item.name || "colección" });
        }
    }
    console.log("OK sintaxis JavaScript de Postman");
    process.exit(0);
}

const offline = input === "--comprobar-bloqueo";
if (!input || (!offline && (!folders.length || folders.some(folder => !groups.includes(folder))))) {
    console.error("Uso: node scripts/ejecutar_postman.cjs <entorno privado> <carpeta> [<carpeta> ...]");
    process.exit(1);
}

const newman = require("newman");
let selected = 0;
let sent = 0;
let omitted = 0;

newman.run({
    collection,
    environment: offline ? example : input,
    folder: offline ? groups : folders,
    ignoreRedirects: true,
    timeoutRequest: 20000,
    timeoutScript: 10000,
    reporters: [],
}, (error, summary) => {
    if (error || !summary || summary.error) {
        console.error("Newman falló antes de completar la ejecución. Revisar el entorno local.");
        process.exitCode = 1;
        return;
    }
    const failed = summary.run.failures.length;
    console.log(`Seleccionadas ${selected} · solicitudes ${sent} · omitidas ${omitted} · aserciones ${summary.run.stats.assertions.total} · fallos ${failed}`);
    if (offline) {
        if (selected !== collection.item.flatMap(folder => folder.item).length || sent || omitted !== selected || failed) {
            console.error("El entorno de ejemplo debe omitir todas las solicitudes.");
            process.exitCode = 1;
        }
    } else if (failed || !sent || omitted || sent + omitted !== selected) {
        process.exitCode = 1;
    }
}).on("beforeItem", () => {
    selected++;
}).on("console", (_error, args) => {
    const message = args.messages[0];
    if (typeof message === "string" && message.startsWith("NO EJECUTADA | ")) {
        omitted++;
        if (!offline) console.log(message);
    }
}).on("request", (error, args) => {
    sent++;
    if (!offline) console.log(`${error ? "ERROR DE TRANSPORTE" : args.response?.code} | ${args.item.name}`);
}).on("assertion", (error, args) => {
    if (error && !offline) console.error(`FALLO | ${args.item.name} | ${args.assertion}`);
}).on("exception", (_error, args) => {
    if (!offline) console.error(`ERROR DE SCRIPT | ${args.item?.name || "colección"}`);
});
