# Deployment status — kiro-langfuse-eval-review

**Status: DEPLOYED**

- Project: `kiro-langfuse-eval-review`
- Account: `Kimisme9386@gmail.com's Account` (`d2fdb3684575e76cf1be3d922daddebc`)
- Live URL (English): **https://kiro-langfuse-eval-review.pages.dev**
- Live URL (Traditional Chinese): **https://kiro-langfuse-eval-review.pages.dev/index-zh.html** (each page links to the other via the language-switch pill in the header)
- This deployment's direct URL: https://15e8d6c8.kiro-langfuse-eval-review.pages.dev
- Deployed from: `labs/kiro-langfuse-eval/pages/{index.html,index-zh.html}` (two static files, no build step)

## Redeploy (reuse this same project — do not create a second one)

```bash
cd /home/node/study-vault
npx wrangler pages deploy labs/kiro-langfuse-eval/pages \
  --project-name kiro-langfuse-eval-review \
  --branch main
```

## Notes

- Auth was via `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` env vars (the token initially lacked "Account Settings: Read", which made `wrangler whoami` unable to list accounts until `CLOUDFLARE_ACCOUNT_ID` was also set).
- Wrangler printed a warning about uncommitted git changes in the working directory; this did not block the deploy and needed no action.
