# Azure: secretos, permisos y despliegue

Esta guía explica cómo se configura cada microservicio en Azure. Los nombres concretos
(suscripción, Key Vault, secretos, identidades) no van aquí porque el repo es público: se
consultan en el portal o se piden por el canal privado del equipo.

## Secretos

Ningún secreto va en el código ni en el repo. Todos están en el Key Vault del proyecto
(con RBAC) y se nombran `Servicio--Nombre`.

Cada App Service los lee con su identidad administrada, que necesita el rol **Key Vault
Secrets User** sobre el Key Vault. En las app settings se referencian así:

```
@Microsoft.KeyVault(VaultName=<key vault>;SecretName=<secreto>)
```

En el portal, la app setting tiene que quedar con estado **Resolved**. Si dice otra cosa,
casi siempre falta el rol o el nombre del secreto está mal escrito.

Qué guarda cada servicio en el Key Vault:

| Servicio | Secretos |
|---|---|
| Usuarios | Cadena de conexión de MongoDB |
| CVs | Cadena de conexión de MongoDB, llave de Gemini, envío a Service Bus |
| Ofertas y Postulaciones | Envío a Service Bus |
| Brecha y Cursos | Contraseña de PostgreSQL |
| Notificaciones | MongoDB, lectura de Service Bus, SignalR, service account de Firebase |

La service account de Firebase es solo para mandar push. App Distribution usa otra.

## Service Bus

Los servicios publican eventos en una cola que escucha Notificaciones. Cada lado usa una
regla de acceso distinta:

| Quién | Permiso |
|---|---|
| CVs, Ofertas y Postulaciones | Solo **Send** |
| Notificaciones | Solo **Listen** |

El esquema de cada evento está en
`cvexpert-ms-notificaciones/docs/contratos/evento-notificacion.schema.json`.

## Permisos del equipo

Cada integrante puede crear y configurar recursos y secretos en el grupo del proyecto,
pero **no asignar roles**. Asignar un rol (por ejemplo, darle a un App Service acceso al
Key Vault, o a un pipeline permiso para desplegar) lo hace el Owner de la suscripción.

## Despliegue con GitHub Actions (OIDC)

Cada microservicio despliega con su propia app de Entra, sin contraseñas:

- **Rol:** Website Contributor **solo sobre su App Service**, no sobre el grupo.
- **Secrets del repo:** `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`.
- **Federated credential:** los repos de la organización usan el **subject inmutable** de
  GitHub, que incluye el ID de la organización y el del repo:

  ```
  repo:<org>@<id de la org>/<repo>@<id del repo>:ref:refs/heads/main
  repo:<org>@<id de la org>/<repo>@<id del repo>:environment:<environment>
  ```

  El prefijo exacto sale de
  `gh api repos/<org>/<repo>/actions/oidc/customization/sub -q .sub_claim_prefix`. Con el
  formato viejo (`repo:<org>/<repo>:...`) el login falla con `AADSTS700213`.
