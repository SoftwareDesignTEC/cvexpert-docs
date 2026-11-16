#!/usr/bin/env node
// Transporte en loopback con respuestas simuladas; no usa servicios CVExpert.
const { createServer } = require("node:http");
const { readFileSync, writeFileSync, mkdtempSync, unlinkSync, rmdirSync } = require("node:fs");
const { tmpdir } = require("node:os");
const { join } = require("node:path");
const assert = require("node:assert/strict");
const newman = require("newman");

const root = join(__dirname, "..");
const fixtures = mkdtempSync(join(tmpdir(), "cvexpert-multipart-"));
const collection = JSON.parse(readFileSync(join(root, "postman/cvexpert.postman_collection.json"), "utf8"));
collection.item = collection.item.filter(folder => folder.name === "Fotografías de CV");
const png = join(fixtures, "synthetic.png");
const txt = join(fixtures, "unsupported.txt");
const big = join(fixtures, "oversize.png");
writeFileSync(png, "SYNTHETIC_IMAGE_BYTES");
writeFileSync(txt, "SYNTHETIC_TEXT");
writeFileSync(big, Buffer.alloc(5 * 1024 * 1024 + 1, 65));

let requests = 0;
const server = createServer((req, res) => {
    const chunks = [];
    req.on("data", chunk => chunks.push(chunk));
    req.on("end", () => {
        requests++;
        const content = Buffer.concat(chunks);
        assert.match(req.headers["content-type"], /^multipart\/form-data; boundary=/);
        assert.match(content.toString("utf8", 0, 350), /name="file"; filename="/);
        let code = 201;
        let error;
        if (!req.headers["x-user-id"]) {
            code = 401;
            error = "Unauthorized";
        } else if (content.includes(Buffer.from("Content-Type: text/plain"))) {
            code = 415;
            error = "UnsupportedMediaType";
        } else if (content.length > 5 * 1024 * 1024) {
            code = 413;
            error = "PayloadTooLarge";
        } else {
            assert.ok(content.includes(Buffer.from("SYNTHETIC_IMAGE_BYTES")));
        }
        res.writeHead(code, { "content-type": "application/json" });
        res.end(JSON.stringify(code === 201
            ? { url: "https://fixture.invalid/synthetic.png" }
            : { statusCode: code, error, message: "Synthetic response; transport test only" }));
    });
});

server.listen(0, "127.0.0.1", () => {
    const values = {
        target: "local",
        allowDirect: "true",
        allowWrites: "true",
        allowUploads: "true",
        cvsBaseUrl: "http://127.0.0.1:" + server.address().port,
        localUserId: "synthetic-user",
        localUserEmail: "synthetic@example.invalid",
        fixturePhotoPath: png,
        fixtureUnsupportedPhotoPath: txt,
        fixtureOversizePhotoPath: big,
    };
    newman.run({
        collection,
        environment: { values: Object.entries(values).map(([key, value]) => ({ key, value, enabled: true })) },
        reporters: [],
        timeoutRequest: 5000,
    }, (error, summary) => {
        server.close();
        for (const file of [png, txt, big]) unlinkSync(file);
        rmdirSync(fixtures);
        if (error) throw error;
        console.log(`TRANSPORTE SINTETICO: solicitudes ${requests}, aserciones ${summary.run.stats.assertions.total}, fallos ${summary.run.failures.length}`);
        for (const failure of summary.run.failures) console.log(failure.source.name + ": " + failure.error.message);
        if (requests !== 4 || summary.run.failures.length) process.exitCode = 1;
    });
});
