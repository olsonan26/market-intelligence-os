export async function GET() {
  return Response.json({
    status: "healthy",
    mode: "fixture",
    liveAuthority: false,
    sources: { market: "fresh", macro: "fresh", news: "degraded" },
    checkedAt: "2026-08-27T12:24:00Z",
  });
}
