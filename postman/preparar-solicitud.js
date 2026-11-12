const cases = JSON.parse(pm.collectionVariables.get("configuracionCasos"));
const config = cases[pm.info.requestName];
const env = key => pm.environment.get(key);
const value = key => String(pm.variables.get(key) ?? "");
const flag = key => env(key) === "true";
const isLocal = env("target") === "local";
const tokenKeys = { user: "googleIdToken", admin: "adminGoogleIdToken",
    fresh: "freshGoogleIdToken", other: "otherGoogleIdToken" };
const directIdentities = { user: "localUser", admin: "localAdmin",
    fresh: "localFresh", other: "localOther" };

function omission() {
    if (!config) return "caso sin configuración";
    for (const key of config.reset) pm.variables.set(key, "");
    if (!["apim", "local"].includes(env("target"))) return "target debe ser apim o local";
    if (config.mode && config.mode !== env("target")) return "caso reservado para " + config.mode;
    const base = String(env(isLocal ? config.service + "BaseUrl" : "apiBaseUrl") || "").replace(/\/$/, "");
    if (isLocal) {
        if (!flag("allowDirect") || !/^https?:\/\/(localhost|127\.0\.0\.1|\[::1\])(:\d+)?$/.test(base)) {
            return "backend directo requiere allowDirect=true y una base loopback";
        }
    } else if (!flag("enableApim") || !/^https:\/\/[a-zA-Z0-9.-]+(?::\d+)?(?:\/[a-zA-Z0-9._~-]+)*$/.test(base)) {
        return "APIM requiere enableApim=true y una base HTTPS revisada";
    }
    if (config.writes && (!flag("allowWrites") ||
        (!isLocal && env("testApiBaseUrl") !== base))) {
        return "operación con efectos requiere allowWrites=true y entorno aislado";
    }
    if (isLocal && config.path.endsWith("/hub/negotiate") && !flag("localSignalR")) {
        return "el escenario requiere negociar con Azure SignalR configurado";
    }
    if (isLocal && config.service === "brecha-cursos" && config.path.startsWith("/skills-gap") && config.role !== "none") {
        return "Brecha requiere certificado verificado, incluso con el bypass local del catálogo";
    }
    if (!isLocal && config.requiresApimJobRole && !flag("allowApimJobAdmin")) {
        return "verificar propagación del rol en ofertas y habilitar allowApimJobAdmin";
    }
    if (config.role === "admin" && !flag("allowAdmin")) return "requiere allowAdmin=true";
    if (config.needs.some(key => !value(key))) return "faltan datos de prueba o un paso previo";

    if (config.bodyVars.some(key => /["\\\x00-\x1f]/.test(value(key)))) {
        return "una variable de cuerpo contiene caracteres sin escapar";
    }
    const role = config.role;
    pm.request.headers.remove("Authorization");
    for (const name of ["X-User-Id", "X-User-Email", "X-User-Role", "X-ARR-ClientCert"]) {
        pm.request.headers.remove(name);
    }
    if (isLocal && role in directIdentities && config.identity) {
        const prefix = directIdentities[role];
        if (!env(prefix + "Id") || !env(prefix + "Email")) return "falta identidad local de pruebas";
        pm.request.headers.upsert({ key: "X-User-Id", value: env(prefix + "Id") });
        pm.request.headers.upsert({ key: "X-User-Email", value: env(prefix + "Email") });
        if (role === "admin") pm.request.headers.upsert({ key: "X-User-Role", value: "admin" });
    }
    if (!isLocal && role !== "none") {
        const token = role === "invalid" ? "token-invalido" : env(tokenKeys[role]);
        if (!token) return "falta token para el rol de la solicitud";
        pm.request.headers.upsert({ key: "Authorization", value: "Bearer " + token });
    }
    let route = isLocal || config.published ? config.path : "";
    if (!isLocal && env("apimRouteOverrides")) {
        let overrides;
        try {
            overrides = JSON.parse(env("apimRouteOverrides"));
        } catch (error) {
            return "apimRouteOverrides debe ser un objeto JSON";
        }
        if (!overrides || typeof overrides !== "object" || Array.isArray(overrides)) {
            return "apimRouteOverrides debe ser un objeto JSON";
        }
        route = overrides[config.operation] ?? route;
    }
    if (!route) return "ruta APIM sin registro; requiere mapeo explícito del entorno";
    if (typeof route !== "string" || !/^\/(?!\/)[a-zA-Z0-9_~./{}-]+$/.test(route) || route.includes("..")) {
        return "ruta relativa inválida";
    }
    for (const [parameter, variable] of Object.entries(config.pathVars)) {
        const marker = "{" + parameter + "}";
        if (!route.includes(marker)) return "la ruta no conserva el parámetro " + parameter;
        route = route.replace(marker, encodeURIComponent(value(variable)));
    }
    if (/[{}]/.test(route)) return "la ruta tiene parámetros sin resolver";
    pm.variables.set("__base", base);
    pm.variables.set("__route", route);
}

const reason = omission();
if (reason) {
    console.warn("NO EJECUTADA | " + pm.info.requestName + " | " + reason);
    pm.execution.skipRequest();
}
