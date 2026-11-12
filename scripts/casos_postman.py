"""Flujos, cuerpos y aserciones de negocio para la colección central."""
import json
from functools import cache

from sincronizar_contratos import ROOT


@cache
def original(service, name):
    source = ROOT / f"postman/originales/{service}.postman_collection.json"

    def requests(items):
        for item in items:
            if "item" in item:
                yield from requests(item["item"])
            else:
                yield item

    items = json.loads(source.read_text(encoding="utf-8"))["item"]
    item = next(item for item in requests(items) if item["name"] == name)
    return json.loads(item["request"]["body"]["raw"])


def case(service, method, path, **options):
    return {"key": (service, method, path), **options}


def u(method, path, **options):
    return case("usuarios", method, path, **options)


def c(method, path, **options):
    return case("cvs", method, path, **options)


def o(method, path, **options):
    return case("ofertas-postulaciones", method, path, **options)


def b(method, path, **options):
    return case("brecha-cursos", method, path, **options)


def n(method, path, **options):
    return case("notificaciones", method, path, **options)


def cv_update(name):
    return original("cvs", name)


def offers(name):
    return original("ofertas-postulaciones", name)


def cv_title(name):
    return cv_update(name)["title"]


CV_CREATE = "POST /cvs"
CV_UPDATE = "PUT /cvs/:id"
JOB_CREATE = "Crear oferta (admin)"
JOB_UPDATE = "Editar oferta (admin)"
TEMPLATE = "/notifications/templates/{type}/{language}"


def groups():
    return {
        "Lecturas": [
            u("GET", "/legal/privacy"),
            u("GET", "/legal/terms"),
            u("GET", "/help"),
            c("GET", "/cvs"),
            c("GET", "/templates"),
            c("GET", "/templates/{id}", path_vars={"id": "fixtureTemplateId"}),
            o("GET", "/jobs"),
            o("GET", "/jobs/{id}", path_vars={"id": "fixtureJobId"}),
            o("GET", "/applications"),
            o("GET", "/alerts"),
            b("GET", "/courses"),
            n("GET", "/notifications"),
            n("GET", "/notifications/unread-count"),
            n("POST", "/notifications/hub/negotiate", query={"negotiateVersion": "1"}),
        ],
        "Perfil y alertas": [
            u("GET", "/profiles/{id}", writes=True, checks={"id": "{{profileId}}"}),
            u("PUT", "/profiles/{id}", body={"fullName": "Perfil de prueba"}, checks={"fullName": "Perfil de prueba"}),
            u("GET", "/profiles/{id}", title="Verificar perfil actualizado", checks={"fullName": "Perfil de prueba"}, writes=True),
            u("GET", "/profiles/{id}/sessions", writes=True),
            u("GET", "/profiles/{id}/export", writes=True),
            o("PUT", "/alerts", body=offers("Guardar alertas y perfil"), checks={"enabled": True, "minMatch": 70}),
            o("GET", "/alerts", title="Verificar alertas guardadas", checks={"enabled": True, "minMatch": 70}),
        ],
        "Ciclo de CV": [
            c("GET", "/templates", title="Seleccionar plantilla del catálogo", capture_first="runCvTemplate", reset=["runCvId", "runCvTemplate"]),
            c("POST", "/cvs", body=cv_update(CV_CREATE), capture={"id": "runCvId"}, checks={"title": cv_title(CV_CREATE)}),
            c("GET", "/cvs/{id}", path_vars={"id": "runCvId"}, checks={"title": cv_title(CV_CREATE), "id": "{{runCvId}}"}),
            c("PUT", "/cvs/{id}", path_vars={"id": "runCvId"}, body=cv_update(CV_UPDATE), checks={"title": cv_title(CV_UPDATE), "id": "{{runCvId}}"}),
            c("GET", "/cvs/{id}", title="Verificar CV actualizado", path_vars={"id": "runCvId"}, checks={"title": cv_title(CV_UPDATE), "id": "{{runCvId}}"}),
            c("DELETE", "/cvs/{id}", path_vars={"id": "runCvId"}),
            c("GET", "/cvs/{id}", title="Verificar eliminación de CV", path_vars={"id": "runCvId"}, status=[404]),
        ],
        "Experiencia laboral": [
            c("POST", "/cvs/ai/expand-experience", body=original("cvs", "POST /cvs/ai/expand-experience")),
            c("POST", "/cvs/ai/translate-experience", body=original("cvs", "POST /cvs/ai/translate-experience")),
        ],
        "Administración de ofertas": [
            o("POST", "/jobs", body=offers(JOB_CREATE), capture={"id": "runJobId"}, reset=["runJobId"], checks={"title": offers(JOB_CREATE)["title"]}),
            o("GET", "/jobs/{id}", title="Verificar oferta creada", path_vars={"id": "runJobId"}, checks={"id": "{{runJobId}}", "title": offers(JOB_CREATE)["title"]}),
            o("PUT", "/jobs/{id}", path_vars={"id": "runJobId"}, body=offers(JOB_UPDATE), checks={"title": offers(JOB_UPDATE)["title"]}),
            o("GET", "/jobs/{id}", title="Verificar oferta actualizada", path_vars={"id": "runJobId"}, checks={"title": offers(JOB_UPDATE)["title"]}),
            o("DELETE", "/jobs/{id}", path_vars={"id": "runJobId"}),
            o("GET", "/jobs/{id}", title="Verificar eliminación de oferta", path_vars={"id": "runJobId"}, status=[404]),
        ],
        "Ciclo de postulaciones": [
            o("POST", "/applications", body={"jobOfferId": "{{fixtureJobId}}", "notes": "Me interesa"}, capture={"id": "runApplicationId"}, reset=["runApplicationId"], checks={"jobOfferId": "{{fixtureJobId}}", "status": "applied"}),
            o("POST", "/applications", title="Conflicto por postulación duplicada", body={"jobOfferId": "{{fixtureJobId}}"}, needs=["runApplicationId"], status=[409]),
            o("GET", "/applications/{id}", path_vars={"id": "runApplicationId"}, checks={"id": "{{runApplicationId}}", "jobOfferId": "{{fixtureJobId}}"}),
            o("GET", "/applications/{id}", title="Otra cuenta sin acceso", path_vars={"id": "runApplicationId"}, role="other", status=[404]),
            o("PUT", "/applications/{id}", path_vars={"id": "runApplicationId"}, body=offers("Mover mi tarjeta"), checks={"status": "in-progress"}),
            o("PUT", "/admin/applications/{id}/status", path_vars={"id": "runApplicationId"}, body=offers("Cambiar estado (admin)"), checks={"status": "interview"}),
            o("GET", "/applications/{id}", title="Verificar estado administrativo", path_vars={"id": "runApplicationId"}, checks={"status": "interview"}),
            o("DELETE", "/applications/{id}", path_vars={"id": "runApplicationId"}),
            o("GET", "/applications/{id}", title="Verificar postulación retirada", path_vars={"id": "runApplicationId"}, status=[404]),
        ],
        "Instantánea y brecha": [
            b("PUT", "/skills-gap/input", body={"skills": [{"skillName": "SQL", "level": "beginner"}]}),
            b("GET", "/skills-gap"),
        ],
        "Directorio y dispositivos": [
            n("PUT", "/notifications/directory/me", body={"language": "es"}, checks={"language": "es"}),
            n("PUT", "/notifications/directory/me", title="Verificar cambio de idioma", body={"language": "en"}, checks={"language": "en"}),
            n("PUT", "/notifications/directory/me", title="Restablecer idioma de prueba", body={"language": "es"}, checks={"language": "es"}),
            n("POST", "/notifications/devices", body={"token": "{{fixtureDeviceToken}}", "platform": "android"}, capture={"token": "runDeviceToken"}, reset=["runDeviceToken"], checks={"token": "{{fixtureDeviceToken}}", "platform": "android"}),
            n("POST", "/notifications/devices", title="Registrar el mismo token", needs=["runDeviceToken"], body={"token": "{{runDeviceToken}}", "platform": "android"}, status=[200], checks={"token": "{{runDeviceToken}}"}),
            n("DELETE", "/notifications/devices/{token}", path_vars={"token": "runDeviceToken"}),
            n("DELETE", "/notifications/devices/{token}", title="Confirmar baja idempotente", path_vars={"token": "runDeviceToken"}),
        ],
        "Lectura de avisos": [
            n("PATCH", "/notifications/{id}/read", path_vars={"id": "fixtureNotificationId"}, checks={"id": "{{fixtureNotificationId}}", "read": True}),
            n("POST", "/notifications/read-all"),
            n("GET", "/notifications/unread-count", title="Verificar contador sin pendientes", checks={"count": 0}),
        ],
        "Administración de plantillas": [
            n("GET", "/notifications/templates", template=True),
            n("GET", TEMPLATE, template=True),
            n("PUT", TEMPLATE, body={"title": "Aviso de prueba", "body": "El estado de tu postulación cambió."}, template=True, updated_template=True),
            n("GET", TEMPLATE, title="Verificar plantilla editada", template=True, updated_template=True, checks={"title": "Aviso de prueba", "body": "El estado de tu postulación cambió."}),
        ],
        "Negativas": [
            b("GET", "/courses", title="Paginación inválida", query={"page": "0"}, status=[400]),
            b("GET", "/skills-gap", title="Sin instantánea", role="fresh", status=[409], checks={"error": "SKILLS_INPUT_REQUIRED"}),
            n("GET", "/notifications/templates", title="Usuario sin rol administrativo", role="user", status=[403]),
            n("PUT", "/notifications/directory/me", title="Idioma inválido", body={"language": "fr"}, status=[400]),
            u("GET", "/profiles/{id}", title="Identidad ajena", role="other", path_vars={"id": "profileId"}, status=[403], writes=True),
            o("POST", "/jobs", title="Usuario sin permiso para crear ofertas", body=offers(JOB_CREATE), role="user", status=[403]),
            o("PUT", "/alerts", title="Umbral inválido", body=offers("Guardar alertas inválidas"), status=[400]),
            c("POST", "/cvs", title="CV sin campos obligatorios", body={"title": "CV incompleto"}, status=[400]),
        ],
        "APIM - Rechazo de identidad": [
            c("GET", "/cvs", title="APIM sin token", role="none", mode="apim", status=[401], status_only=True),
            c("GET", "/cvs", title="APIM con token inválido", role="invalid", mode="apim", status=[401], status_only=True),
        ],
        "Backend directo - Brecha": [
            b("GET", "/health", mode="local"),
            b("GET", "/skills-gap", title="Backend sin certificado", role="none", mode="local", status=[403], checks={"error": "APIM_CERTIFICATE_REQUIRED"}),
        ],
        "Backend directo - Notificaciones": [
            n("GET", "/health", mode="local"),
            n("GET", "/notifications", title="Backend sin identidad inyectada", role="none", mode="local", status=[401]),
        ],
    }
