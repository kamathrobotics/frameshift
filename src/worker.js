export default {
  async fetch(request, env) {
    // Static assets are served automatically by the [assets] config in wrangler.toml.
    // This worker handles any requests that don't match a static file.
    return new Response('Not Found', { status: 404 });
  },
};
