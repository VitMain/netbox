# Content Security Policy

A [Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP) (CSP) tells the browser which sources a page may load scripts, images, fonts, and other resources from. NetBox does not send one by default. To send one, define it with the [`SECURE_CSP`](../configuration/security.md#secure_csp) or [`SECURE_CSP_REPORT_ONLY`](../configuration/security.md#secure_csp_report_only) configuration parameter.

NetBox's own pages are written to work under a strict script policy. Every `<script>` element NetBox renders carries the per-request nonce, and NetBox does not use inline event handler attributes or evaluate strings as code. This applies to scripts only. NetBox makes no equivalent promise for styles: it renders inline `<style>` elements and `style=` attributes, and none of them carry a nonce.

## Example policy

The policy below is an example, not a default. It has been checked against the pages that need no outside setup: the login page, object lists and detail pages, cable traces, Markdown images, GraphiQL, the Swagger and Redoc API documentation, and the REST API's browsable view.

```python
from django.utils.csp import CSP

SECURE_CSP = {
    'default-src': [CSP.SELF],
    'script-src': [CSP.SELF, CSP.NONCE, 'https://static.copilot.netboxlabs.ai'],
    'style-src': [CSP.SELF, CSP.UNSAFE_INLINE, 'https://fonts.googleapis.com'],
    'font-src': [CSP.SELF, 'data:', 'https://fonts.gstatic.com'],
    'img-src': [CSP.SELF, 'data:', 'https:'],
    'connect-src': [CSP.SELF],
    'worker-src': [CSP.SELF, 'blob:'],
    'base-uri': [CSP.SELF],
}
```

The policy has no `object-src` directive because cable traces embed their SVG in an `<object>` element, which falls back to `default-src 'self'`.

To try it without enforcing it, assign the same dictionary to `SECURE_CSP_REPORT_ONLY` instead. See [Testing a policy](#testing-a-policy) below.

## What each directive allows

* `script-src` allows scripts served by NetBox, scripts carrying the request's nonce, and the loader script for NetBox Copilot. Copilot is only loaded when it is enabled. The loader may request further hosts of its own, which this page does not cover.
* `style-src` allows inline styles, plus Google Fonts stylesheets, which the Redoc page loads. See [Styles](#styles) below.
* `font-src` allows NetBox's own fonts, the `data:` fonts embedded in the GraphiQL stylesheet, and `fonts.gstatic.com` for Redoc.
* `img-src` allows `https:` so that Markdown images hosted elsewhere keep loading. NetBox keeps `http` and `https` image sources in rendered Markdown from any host. You can replace `https:` with a list of named hosts, but images from every other host will stop loading.
* `connect-src` allows requests back to NetBox. The REST API and GraphQL tools, the Swagger try-it-out feature, and the start of a single sign-on login all depend on it.
* `worker-src` allows the web workers GraphiQL starts from NetBox's own files, and the `blob:` worker Redoc starts.
* `base-uri` stops an injected `<base>` element from redirecting relative URLs.

Other deployments need more. If media files are served from another host, add it to `img-src`, and to `media-src` or other directives if the files are not images. If `STATIC_URL` points at another host, add that host to `script-src`, `style-src`, `font-src`, and `img-src`.

## Styles

NetBox's nonce rule covers scripts only, and the example policy does not restrict inline styles. The reasons are that the nonce requirement exists to stop injected code from running, injected styles cannot run code, and NetBox renders a few dozen inline `style=` attributes, many with computed values such as colors and utilization widths. A style attribute cannot carry a nonce. Adding a nonce to `style-src` would also cause browsers to ignore `'unsafe-inline'`, which would block every one of them.

This differs from scripts, where NetBox supports a strict policy today. A strict `style-src` is not covered by this page.

## Stronger script policies

The example uses `'self'` plus a nonce. You can add `'strict-dynamic'` to `script-src`, which lets nonced scripts load further scripts and makes browsers ignore `'self'`. It has two trade-offs. Plugin `<script src>` tags that lack a nonce stop working, and any script that Copilot loads is trusted.

## Testing a policy

Start with `SECURE_CSP_REPORT_ONLY`. The browser reports every violation in its developer console without blocking anything. Browse the pages your users rely on, including any plugin pages, and watch the console. When it stays quiet, move the policy to `SECURE_CSP`.

Test with `DEBUG` set to `False`. The Django debug toolbar and GraphiQL's debug integration inject inline scripts that a nonce policy reports.

!!! note "Single sign-on"
    Redirect-based SSO logins need `connect-src 'self'`, which the example includes. See the [authentication overview](authentication/overview.md) for the SSO requirements.
