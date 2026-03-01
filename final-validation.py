"""
Day 5: Final System Validation & Production Readiness
Content Generation Platform - YouTube Focus
"""

import asyncio
import aiohttp
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any

BASE_URL = "http://localhost:5000"

class ProductionValidator:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0

    def log(self, test: str, status: bool, detail: str = ""):
        icon = "✅" if status else "❌"
        msg = f"{icon} {test}"
        if detail:
            msg += f" — {detail}"
        print(msg)
        self.results.append({"test": test, "passed": status, "detail": detail})
        if status:
            self.passed += 1
        else:
            self.failed += 1

    async def run_all(self):
        print("\n" + "="*60)
        print("  CONTENT PLATFORM — FINAL PRODUCTION VALIDATION")
        print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")

        async with aiohttp.ClientSession() as session:
            await self.validate_health(session)
            await self.validate_intake_form(session)
            await self.validate_agent1(session)
            await self.validate_agent2(session)
            await self.validate_pack_assembly(session)
            await self.validate_download(session)
            await self.validate_performance(session)
            await self.validate_error_handling(session)
            await self.validate_security_headers(session)

        self.print_summary()

    # ── Health Check ──────────────────────────────────────────────
    async def validate_health(self, session):
        print("[ Health & Infrastructure ]")
        try:
            async with session.get(f"{BASE_URL}/health") as r:
                data = await r.json()
                self.log("API health endpoint", r.status == 200, data.get("status"))
                self.log("Redis connection", data.get("redis") == "connected", data.get("redis"))
                self.log("OpenAI API key configured", data.get("openai_configured", False))
                self.log("YouTube API key configured", data.get("youtube_configured", False))
        except Exception as e:
            self.log("Health endpoint reachable", False, str(e))
        print()

    # ── Intake Form Validation ────────────────────────────────────
    async def validate_intake_form(self, session):
        print("[ Intake Form Validation ]")
        # Missing required fields
        try:
            async with session.post(f"{BASE_URL}/api/validate-form",
                                    json={"brand_name": ""}) as r:
                self.log("Rejects empty brand name", r.status == 400)
        except Exception as e:
            self.log("Form validation endpoint", False, str(e))

        # Valid payload
        valid_payload = {
            "brand_name": "TechVision",
            "topic": "AI in everyday life",
            "tone": "professional",
            "style": "educational",
            "video_length": "medium",
            "brand_colors": ["#1A73E8", "#FFFFFF"],
            "platform": "youtube"
        }
        try:
            async with session.post(f"{BASE_URL}/api/validate-form",
                                    json=valid_payload) as r:
                self.log("Accepts valid form payload", r.status == 200)
        except Exception as e:
            self.log("Valid form submission", False, str(e))
        print()

    # ── Agent 1 ───────────────────────────────────────────────────
    async def validate_agent1(self, session):
        print("[ Agent 1 — YouTube Content Generator ]")
        payload = {
            "brand_name": "TechVision",
            "topic": "AI in everyday life",
            "tone": "professional",
            "video_length": "medium"
        }
        try:
            start = time.time()
            async with session.post(f"{BASE_URL}/api/generate-content",
                                    json=payload, timeout=aiohttp.ClientTimeout(total=60)) as r:
                elapsed = round(time.time() - start, 2)
                data = await r.json()
                self.log("Agent 1 returns 200", r.status == 200)
                self.log("Title generated", bool(data.get("title")))
                self.log("Description generated", bool(data.get("description")))
                self.log("Script generated", bool(data.get("script")))
                self.log("Hashtags generated", isinstance(data.get("hashtags"), list))
                self.log("Metadata present", bool(data.get("metadata")))
                self.log(f"Response time acceptable (<30s)", elapsed < 30, f"{elapsed}s")
        except Exception as e:
            self.log("Agent 1 execution", False, str(e))
        print()

    # ── Agent 2 ───────────────────────────────────────────────────
    async def validate_agent2(self, session):
        print("[ Agent 2 — Visual Generator ]")
        payload = {
            "content": {"title": "AI in Everyday Life", "description": "Exploring AI tools"},
            "brand_colors": ["#1A73E8", "#FFFFFF"],
            "style_preference": "modern"
        }
        try:
            async with session.post(f"{BASE_URL}/api/generate-visuals",
                                    json=payload, timeout=aiohttp.ClientTimeout(total=90)) as r:
                data = await r.json()
                self.log("Agent 2 returns 200", r.status == 200)
                self.log("Thumbnail variants generated", len(data.get("variants", [])) >= 2)
                self.log("Brand colors applied", data.get("brand_colors_applied", False))
                self.log("Image URLs present", all("url" in v for v in data.get("variants", [])))
        except Exception as e:
            self.log("Agent 2 execution", False, str(e))
        print()

    # ── Pack Assembly ─────────────────────────────────────────────
    async def validate_pack_assembly(self, session):
        print("[ Social Media Pack Assembly ]")
        payload = {
            "brand_name": "TechVision",
            "topic": "AI in everyday life",
            "tone": "professional",
            "style": "educational",
            "video_length": "medium",
            "brand_colors": ["#1A73E8", "#FFFFFF"],
            "platform": "youtube"
        }
        try:
            async with session.post(f"{BASE_URL}/api/generate",
                                    json=payload, timeout=aiohttp.ClientTimeout(total=120)) as r:
                data = await r.json()
                self.log("Full pack generation returns 200", r.status == 200)
                self.log("Pack ID assigned", bool(data.get("pack_id")))
                self.log("Content included in pack", bool(data.get("content")))
                self.log("Visuals included in pack", bool(data.get("visuals")))
                self.log("Hashtags included", bool(data.get("hashtags")))
                self.log("Optimization tips included", bool(data.get("optimization_tips")))
                self.pack_id = data.get("pack_id")
        except Exception as e:
            self.log("Pack assembly", False, str(e))
            self.pack_id = None
        print()

    # ── Download ──────────────────────────────────────────────────
    async def validate_download(self, session):
        print("[ Pack Download ]")
        if not getattr(self, "pack_id", None):
            self.log("Download test skipped (no pack_id)", False, "depends on pack assembly")
            print()
            return
        try:
            async with session.get(f"{BASE_URL}/api/download/{self.pack_id}") as r:
                self.log("Download endpoint returns 200", r.status == 200)
                self.log("Content-Type is ZIP",
                         "zip" in r.headers.get("Content-Type", "").lower())
                self.log("Content-Disposition header present",
                         "attachment" in r.headers.get("Content-Disposition", "").lower())
        except Exception as e:
            self.log("Pack download", False, str(e))
        print()

    # ── Performance ───────────────────────────────────────────────
    async def validate_performance(self, session):
        print("[ Performance Benchmarks ]")
        try:
            # Cache hit test
            payload = {"brand_name": "TechVision", "topic": "AI in everyday life",
                       "tone": "professional", "video_length": "medium"}
            start = time.time()
            async with session.post(f"{BASE_URL}/api/generate-content",
                                    json=payload, timeout=aiohttp.ClientTimeout(total=30)) as r:
                cached_time = round(time.time() - start, 2)
                data = await r.json()
                self.log("Cache hit response <5s", cached_time < 5, f"{cached_time}s")
                self.log("Cache hit flag present", data.get("cached", False))

            # Metrics endpoint
            async with session.get(f"{BASE_URL}/api/metrics") as r:
                metrics = await r.json()
                self.log("Metrics endpoint available", r.status == 200)
                self.log("Cache hit rate tracked", "cache_hit_rate" in metrics)
        except Exception as e:
            self.log("Performance validation", False, str(e))
        print()

    # ── Error Handling ────────────────────────────────────────────
    async def validate_error_handling(self, session):
        print("[ Error Handling ]")
        try:
            async with session.post(f"{BASE_URL}/api/generate-content",
                                    json={}) as r:
                self.log("Empty payload returns 400", r.status == 400)

            async with session.get(f"{BASE_URL}/api/download/invalid-pack-id") as r:
                self.log("Invalid pack ID returns 404", r.status == 404)

            async with session.get(f"{BASE_URL}/nonexistent-route") as r:
                self.log("Unknown route returns 404", r.status == 404)
        except Exception as e:
            self.log("Error handling validation", False, str(e))
        print()

    # ── Security Headers ──────────────────────────────────────────
    async def validate_security_headers(self, session):
        print("[ Security Headers ]")
        try:
            async with session.get(f"{BASE_URL}/health") as r:
                headers = r.headers
                self.log("X-Content-Type-Options set",
                         headers.get("X-Content-Type-Options") == "nosniff")
                self.log("X-Frame-Options set",
                         bool(headers.get("X-Frame-Options")))
                self.log("X-XSS-Protection set",
                         bool(headers.get("X-XSS-Protection")))
        except Exception as e:
            self.log("Security headers validation", False, str(e))
        print()

    # ── Summary ───────────────────────────────────────────────────
    def print_summary(self):
        total = self.passed + self.failed
        rate = round((self.passed / total) * 100) if total else 0
        print("="*60)
        print(f"  VALIDATION SUMMARY")
        print(f"  Passed : {self.passed}/{total} ({rate}%)")
        print(f"  Failed : {self.failed}/{total}")
        print("="*60)

        if rate >= 90:
            print("\n🚀 SYSTEM IS PRODUCTION READY!\n")
        elif rate >= 70:
            print("\n⚠️  SYSTEM NEEDS MINOR FIXES BEFORE DEPLOYMENT\n")
        else:
            print("\n🛑 SYSTEM NOT READY — CRITICAL ISSUES FOUND\n")

        if self.failed:
            print("Failed tests:")
            for r in self.results:
                if not r["passed"]:
                    print(f"  • {r['test']}: {r['detail']}")

        # Save report
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {"passed": self.passed, "failed": self.failed,
                        "total": total, "pass_rate": rate},
            "results": self.results
        }
        with open("validation-report.json", "w") as f:
            json.dump(report, f, indent=2)
        print("\n📄 Full report saved to validation-report.json")


if __name__ == "__main__":
    validator = ProductionValidator()
    asyncio.run(validator.run_all())
