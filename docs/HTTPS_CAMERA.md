# Camera and HTTPS — why the live demo cannot use a webcam over http://

## The bug the user hit (27 Oct 2026)

Clicking "Start camera" on http://16.171.250.54:8000 gave
"Camera was not allowed — try the demo shelf or upload a photo
instead." That message was wrong: the user had not denied anything.

## Diagnosis (confirmed)

`getUserMedia()` only works in a secure context: `https://` or
`localhost`. The live EC2 demo is served over plain `http://` on a
bare IP address, so in Chrome/Safari/Firefox `navigator.mediaDevices`
is `undefined` on that page and the browser never shows a permission
prompt at all. The old code caught that error and reported it as a
denial. Evidence: the same dashboard code works on `localhost`
(where the context is secure); on the EC2 `http://` URL it fails
before any prompt, in every browser.

## What the dashboard does now (shipped in this fix)

- On page load over `http://`, a plain-language note explains the
  block and points to the working paths.
- Clicking "Start camera" over `http://` says so explicitly, instead
  of claiming permission was denied. Denied permission
  (`NotAllowedError`) and no camera (`NotFoundError`) now get their
  own, different messages.
- Camera-free paths are primary on `http://`: "Try the demo shelf",
  "Upload a photo or video" (video checks its first frame only),
  and the new "Set full shelf from a photo" button, which sets the
  full-shelf baseline from a photo — so a judge can run the whole
  Full → Low/Gap → alert → restock → Full journey with no camera.
- To use the live camera, run the same app on your own computer
  (`localhost`): `uvicorn app.main:app --port 8000`, then open
  http://localhost:8000. That context is secure, so the camera works.

## Why HTTPS is not simply switched on for EC2

A public certificate authority (e.g. Let's Encrypt) will not issue a
certificate for a bare IP address; it requires a domain name with DNS
pointing at the server. So HTTPS on EC2 needs, in order: a domain,
DNS to 16.171.250.54, and a reverse proxy (Caddy/nginx) terminating
TLS in front of port 8000. That is doable, but it is a
demo-breaking change if done wrong hours before a deadline, and it
needs a domain the project does not currently have.

## Options, in order of safety before the deadline

1. Ship the graceful `http://` path (done in this fix) + localhost
   instructions. No risk to the live demo. Recommended for judging.
2. Optional: put a free tunnel in front of EC2:8000 (e.g. Cloudflare
   Tunnel or ngrok) to get an `https://` URL for the camera. This
   gives a working camera without buying a domain, but the tunnel
   URL is a second link judges must use, free tunnels can change or
   rate-limit, and it must be verified end-to-end before it is put
   on Devpost. Do not advertise a tunnel URL until it is verified
   playing with the camera.
3. After the deadline, if a domain is wanted: point the domain at
   EC2, put Caddy in front of the container with automatic HTTPS,
   verify camera + /health + /api/demo, then update Devpost.

## Do NOT claim

- Camera works on the `http://` EC2 link. It does not, by browser
  design, and the dashboard now says so.
- A tunnel or domain HTTPS link works until it has been verified
  with a real camera in a real browser.
