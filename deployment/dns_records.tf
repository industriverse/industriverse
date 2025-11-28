resource "cloudflare_record" "portal" {
  zone_id = var.cloudflare_zone_id
  name    = "portal"
  value   = "cname.vercel-dns.com"
  type    = "CNAME"
  proxied = true
}

resource "cloudflare_record" "api" {
  zone_id = var.cloudflare_zone_id
  name    = "api"
  value   = var.backend_load_balancer_ip
  type    = "A"
  proxied = true
}

resource "cloudflare_record" "pilot" {
  zone_id = var.cloudflare_zone_id
  name    = "pilot"
  value   = var.pilot_container_ip
  type    = "A"
  proxied = true
}

resource "cloudflare_record" "capsules" {
  zone_id = var.cloudflare_zone_id
  name    = "capsules"
  value   = "cname.vercel-dns.com"
  type    = "CNAME"
  proxied = true
}

# Thermodynasty Integration
resource "cloudflare_record" "thermodynasty_app" {
  zone_id = var.thermodynasty_zone_id
  name    = "app"
  value   = "portal.industriverse.ai"
  type    = "CNAME"
  proxied = true
}
