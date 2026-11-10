# Google Cloud deployment

Project: `whatevercooker` (`920895543459`). Region: `us-central1`.
Service: `whatevercooker`.
Direct service URL: https://whatevercooker-na4pphqb2q-uc.a.run.app
Production domains: `whatevercooker.com` and `www.whatevercooker.com`.

## Deployments

Pushes to `main` run `.github/workflows/deploy-google-cloud.yml`: build and smoke-test the Nginx container, push it to Artifact Registry, then deploy Cloud Run.
GitHub uses short-lived Workload Identity Federation credentials. The provider
requires repository ID `1254060273`, owner ID `13527914`, and `refs/heads/main`.
No service-account keys are stored in GitHub or this repository.

For manual deployment with an authorized Google account:

```sh
gcloud auth login
bash scripts/deploy_google.sh
```

The runtime service account `website-runtime` has no project roles. Cloud Run
uses 1 CPU, 256 MiB RAM, request-based CPU allocation, 0 minimum and 3 maximum
instances. Public access is intentional for this public website.

`Dockerfile` stages only the public files listed by `scripts/build_site.py`.
Nginx runs as a non-root user on port 8080. Repository metadata, deployment
scripts, and credentials are not served. Add new top-level public asset
directories to the staging list when necessary.

## Domain and TLS

A global external Application Load Balancer routes to the Cloud Run service
through the `website-neg` serverless NEG and `website-backend` backend service.
The reserved IPv4 address `website-ip` is **35.186.244.47**.
`website-https` uses Google-managed certificate `website-cert-cutover`
(the initial `website-cert` request is temporarily retained during provisioning).
`website-http` redirects port 80 to HTTPS via `http-redirect.yaml`.
The `website-tls` policy requires TLS 1.2 or newer.

GoDaddy records (TTL 600 seconds):

| Type | Name | Value |
| --- | --- | --- |
| A | @ | 35.186.244.47 |
| CNAME | www | whatevercooker.com |

These DNS records are verified at Google and Cloudflare public resolvers.
Preserve email/MX, TXT and other unrelated records. Google-managed certificate
issuance and propagation are still pending; the direct Cloud Run URL works.

Check status:

```sh
gcloud compute ssl-certificates describe website-cert-cutover --global --project=whatevercooker
gcloud run services describe whatevercooker --region=us-central1 --project=whatevercooker
curl -I https://whatevercooker.com/
curl -I https://www.whatevercooker.com/
```

Cloud Run, Cloud Build, Artifact Registry, and the load balancer use the existing
Google Cloud billing account. The load balancer has ongoing charges even when
Cloud Run scales to zero.

## Migration status

Cloud Run deployment, public-file checks, the load balancer HTTP redirect, and
the GitHub deployment workflow passed verification on 2026-11-10.
Workflow run: https://github.com/lanlee/whatever-cooker/actions/runs/42775561954

DNS cutover is verified. The previous hosting project and its deployments were
deleted; the project API confirms 404. Its Git integration and local configuration
are removed. Automatic deployment to Google Cloud is enabled for pushes to
`main` and has passed end-to-end verification.

The remaining step is Google-managed TLS activation and verification of the
custom-domain HTTPS pages. At the latest check, the certificate domain status
was ACTIVE for `www.whatevercooker.com` and PROVISIONING for `whatevercooker.com`.

## Existing content issue

The blog index links to `/blog/ten-minute-meals`, and the sitemap lists
`/blog/fresh-cooked-meals`. Their Markdown sources exist, but this repository
has no generated HTML article pages or article renderer. These pre-existing
routes need a rendering fix; all existing public files are preserved.
