#!/usr/bin/env python3
"""
Enrich startup dataset with market-facing signals for investment review.

Output columns:
1) Latest Funding & Valuation
2) GitHub/OSS Traction
3) AI-Native Competitors
4) Market Sentiment
"""

from __future__ import annotations

import csv
import datetime as dt
import html
import math
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
from urllib.parse import urlparse

import requests


INPUT_PATH = Path(
    "/home/ubuntu/.cursor/projects/workspace/uploads/"
    "2026-02-17-export-Projects-Priorities-100-of-150-analyzed-for-AI-xlsx.csv.txt"
)
OUTPUT_DIR = Path("/workspace/source/startup_market_enrichment/output")

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
)

MONEY_RE = re.compile(
    r"\$ ?([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?|[0-9]+(?:\.[0-9]+)?) ?"
    r"(billion|bn|b|million|mn|m|k)?",
    re.IGNORECASE,
)
ROUND_RE = re.compile(
    r"\b(pre[- ]seed|seed|series [a-z]|series [0-9]|angel|venture round|debt|grant|acqui(?:red|sition)|ipo)\b",
    re.IGNORECASE,
)
G2_RATING_RE = re.compile(
    r"\b([0-5](?:\.[0-9])?)\s*(?:/|out of)\s*5\b", re.IGNORECASE
)

TRUSTED_MARKET_DATA_DOMAINS = {
    "pitchbook.com",
    "my.pitchbook.com",
    "crunchbase.com",
    "cbinsights.com",
    "tracxn.com",
    "dealroom.co",
    "techcrunch.com",
    "venturebeat.com",
    "forbes.com",
    "sifted.eu",
    "eu-startups.com",
    "businesswire.com",
    "prnewswire.com",
    "globenewswire.com",
    "sec.report",
    "sec.gov",
}


def clean_html_text(raw: str) -> str:
    stripped = re.sub(r"<[^>]+>", " ", raw)
    stripped = html.unescape(stripped)
    return " ".join(stripped.split())


def safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    text = text.replace(",", "")
    try:
        return float(text)
    except ValueError:
        return None


def safe_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    match = re.search(r"\d+", text.replace(",", ""))
    if not match:
        return None
    try:
        return int(match.group(0))
    except ValueError:
        return None


def normalize_url(url: str) -> str:
    text = (url or "").strip()
    if not text:
        return ""
    if not text.startswith(("http://", "https://")):
        text = f"https://{text}"
    return text


def host_from_url(url: str) -> str:
    normalized = normalize_url(url)
    if not normalized:
        return ""
    host = urlparse(normalized).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def primary_domain_label(host: str) -> str:
    if not host:
        return ""
    return host.split(".")[0]


def slugify(text: str) -> str:
    lowered = (text or "").lower()
    lowered = re.sub(r"&", " and ", lowered)
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    lowered = lowered.strip("-")
    return lowered


def startup_name_variants(name: str) -> List[str]:
    variants: List[str] = []
    original = (name or "").strip()
    if original:
        variants.append(original)

    base = re.sub(r"\s*\(.*?\)", "", original).strip()
    if base and base not in variants:
        variants.append(base)

    for match in re.findall(r"\((.*?)\)", original):
        for token in re.split(r"[,/]", match):
            token = token.strip()
            if token and token not in variants:
                variants.append(token)
    return variants


def parse_money_to_millions(amount_text: str) -> Optional[float]:
    match = MONEY_RE.search(amount_text or "")
    if not match:
        return None
    raw = float(match.group(1).replace(",", ""))
    unit = (match.group(2) or "").lower()
    if unit in {"billion", "bn", "b"}:
        return raw * 1000.0
    if unit in {"million", "mn", "m"}:
        return raw
    if unit == "k":
        return raw / 1000.0
    # Bare values are ambiguous; return None to avoid false precision.
    return None


def format_millions(amount_m: float) -> str:
    if amount_m >= 1000:
        return f"${amount_m / 1000:.2f}B"
    return f"${amount_m:.1f}M"


def extract_domain_for_display(url: str) -> str:
    host = host_from_url(url)
    return host or "web"


@dataclass
class GithubSignal:
    repo_full_name: str
    stars: int
    pushed_at: str
    confidence: float


class StartupEnricher:
    def __init__(self) -> None:
        self.web = requests.Session()
        self.web.headers.update({"User-Agent": USER_AGENT})

        self.gh = requests.Session()
        self.gh.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "User-Agent": USER_AGENT,
            }
        )
        token = self._gh_token()
        if token:
            self.gh.headers.update({"Authorization": f"Bearer {token}"})

        self._brave_cache: Dict[str, List[Dict[str, str]]] = {}
        self._gh_user_cache: Dict[str, Optional[Dict[str, Any]]] = {}
        self._gh_repo_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._gh_search_cache: Dict[str, List[Dict[str, Any]]] = {}

    @staticmethod
    def _gh_token() -> str:
        try:
            proc = subprocess.run(
                ["gh", "auth", "token"],
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            return ""
        if proc.returncode != 0:
            return ""
        return proc.stdout.strip()

    def _get_with_retries(
        self,
        session: requests.Session,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 20,
        retries: int = 3,
        backoff: float = 1.5,
    ) -> Optional[requests.Response]:
        delay = 1.0
        for attempt in range(retries):
            try:
                resp = session.get(url, params=params, timeout=timeout)
                if resp.status_code in {429, 500, 502, 503, 504}:
                    if attempt < retries - 1:
                        time.sleep(delay)
                        delay *= backoff
                        continue
                return resp
            except requests.RequestException:
                if attempt < retries - 1:
                    time.sleep(delay)
                    delay *= backoff
                    continue
                return None
        return None

    def _github_json(
        self, path: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        resp = self._get_with_retries(
            self.gh,
            f"https://api.github.com{path}",
            params=params,
            timeout=25,
        )
        if resp is None:
            return None
        if resp.status_code != 200:
            return None
        try:
            return resp.json()
        except ValueError:
            return None

    def brave_search(self, query: str) -> List[Dict[str, str]]:
        if query in self._brave_cache:
            return self._brave_cache[query]

        resp = self._get_with_retries(
            self.web,
            "https://search.brave.com/search",
            params={"q": query},
            timeout=25,
        )
        if resp is None or resp.status_code != 200:
            self._brave_cache[query] = []
            return []

        html_text = resp.text
        blocks = html_text.split('data-type="web" data-keynav="true">')[1:9]
        results: List[Dict[str, str]] = []

        for block in blocks:
            href_m = re.search(r'<a href="([^"]+)"', block)
            title_m = re.search(r'<div class="title [^>]*>(.*?)</div>', block, re.S)
            snippet_m = re.search(
                r'<div class="content [^>]*>(.*?)</div>', block, re.S
            )
            if not href_m:
                continue
            url = href_m.group(1).strip()
            title = clean_html_text(title_m.group(1)) if title_m else ""
            snippet = clean_html_text(snippet_m.group(1)) if snippet_m else ""
            if not url:
                continue
            results.append({"url": url, "title": title, "snippet": snippet})

        self._brave_cache[query] = results
        # Mild pacing to avoid triggering search anti-bot protections.
        time.sleep(0.05)
        return results

    def _github_user(self, login: str) -> Optional[Dict[str, Any]]:
        if login in self._gh_user_cache:
            return self._gh_user_cache[login]
        data = self._github_json(f"/users/{login}")
        self._gh_user_cache[login] = data
        return data

    def _github_user_repos(self, login: str) -> List[Dict[str, Any]]:
        if login in self._gh_repo_cache:
            return self._gh_repo_cache[login]
        data = self._github_json(
            f"/users/{login}/repos",
            params={"per_page": 100, "sort": "updated"},
        )
        repos: List[Dict[str, Any]] = data if isinstance(data, list) else []
        self._gh_repo_cache[login] = repos
        return repos

    def _github_repo_search(self, query: str) -> List[Dict[str, Any]]:
        if query in self._gh_search_cache:
            return self._gh_search_cache[query]
        data = self._github_json(
            "/search/repositories",
            params={"q": query, "sort": "stars", "order": "desc", "per_page": 20},
        )
        items = data.get("items", []) if isinstance(data, dict) else []
        self._gh_search_cache[query] = items
        return items

    @staticmethod
    def _is_likely_oss(name: str, description: str) -> bool:
        text = f"{name} {description}".lower()
        keywords = [
            "open source",
            "open-source",
            "oss",
            "framework",
            "kubernetes",
            "k8s",
            "database",
            "sdk",
            "linux",
            "graphql",
            "terraform",
            "iac",
            "infrastructure as code",
            "bazel",
            "developer tool",
            "developer platform",
            "api",
            "feature flag",
            "session replay",
            "serverless",
            "monitoring",
            "observability",
            "self-hosted",
            "ci/cd",
            "query engine",
            "cloud-native",
        ]
        return any(key in text for key in keywords)

    @staticmethod
    def _repo_score(
        repo: Dict[str, Any],
        variants: Sequence[str],
        domain: str,
        domain_label: str,
    ) -> float:
        full_name = (repo.get("full_name") or "").lower()
        description = (repo.get("description") or "").lower()
        homepage = (repo.get("homepage") or "").lower()
        owner = ((repo.get("owner") or {}).get("login") or "").lower()

        score = 0.0
        if not repo.get("fork"):
            score += 1.2
        if not repo.get("archived"):
            score += 0.8

        stars = int(repo.get("stargazers_count") or 0)
        score += min(3.0, math.log10(stars + 1))

        if domain and domain in homepage:
            score += 5.0
        if domain_label and (
            domain_label in full_name or domain_label in owner or domain_label in homepage
        ):
            score += 2.0

        for variant in variants:
            slug = slugify(variant)
            if not slug:
                continue
            compact = slug.replace("-", "")
            if slug in full_name or compact in full_name.replace("-", ""):
                score += 1.6
            if slug in owner or compact in owner.replace("-", ""):
                score += 1.3
            if slug in description or compact in description.replace("-", ""):
                score += 0.6
        return score

    @staticmethod
    def _repo_is_plausible_match(
        repo: Dict[str, Any],
        domain: str,
        domain_label: str,
        candidate_logins: Sequence[str],
        variants: Sequence[str],
    ) -> bool:
        owner = ((repo.get("owner") or {}).get("login") or "").lower()
        full_name = (repo.get("full_name") or "").lower()
        description = (repo.get("description") or "").lower()
        homepage = (repo.get("homepage") or "").lower()
        stars = int(repo.get("stargazers_count") or 0)

        variant_slugs = [slugify(v) for v in variants if slugify(v)]
        owner_match = owner in set(candidate_logins)
        homepage_domain_match = bool(domain and domain in homepage)
        strict_label_match = bool(
            domain_label
            and (
                owner == domain_label
                or full_name.startswith(f"{domain_label}/")
            )
        )
        variant_match = any(s in full_name or s in description for s in variant_slugs)

        # Accept strong matches only; this avoids common-word collisions
        # (e.g., "middleware" matching unrelated repos).
        if homepage_domain_match:
            return True
        if strict_label_match and stars >= 5:
            return True
        if owner_match and variant_match and stars >= 5:
            return True
        return False

    def github_signal(
        self,
        startup_name: str,
        startup_url: str,
        description: str,
    ) -> Tuple[Optional[GithubSignal], bool]:
        host = host_from_url(startup_url)
        domain_label = primary_domain_label(host)
        variants = startup_name_variants(startup_name)
        likely_oss = self._is_likely_oss(startup_name, description)

        login_candidates: List[str] = []
        if domain_label:
            login_candidates.append(domain_label)
            login_candidates.append(f"{domain_label}-io")
            login_candidates.append(f"{domain_label}io")
            login_candidates.append(f"{domain_label}-labs")
        for variant in variants:
            s = slugify(variant)
            if s:
                login_candidates.append(s)
                login_candidates.append(s.replace("-", ""))
                login_candidates.append(f"{s}-io")

        dedup_login: List[str] = []
        seen = set()
        for c in login_candidates:
            if not c or c in seen:
                continue
            seen.add(c)
            dedup_login.append(c)

        candidate_repos: Dict[int, Dict[str, Any]] = {}

        # Conservative search queries only (avoids user endpoint throttling).
        search_queries: List[str] = []
        if host:
            search_queries.append(f"\"{host}\" in:readme,description")
        if domain_label:
            search_queries.append(f"{domain_label} in:name,description")
        if not domain_label:
            primary_query_term = variants[0] if variants else startup_name
            search_queries.append(f"{primary_query_term} in:name,description")

        for query in search_queries[:2]:
            repos = self._github_repo_search(query)
            for repo in repos:
                if "id" in repo:
                    candidate_repos[int(repo["id"])] = repo

        best_repo: Optional[Dict[str, Any]] = None
        best_score = -1.0
        for repo in candidate_repos.values():
            if not self._repo_is_plausible_match(
                repo, host, domain_label, dedup_login, variants
            ):
                continue
            score = self._repo_score(repo, variants, host, domain_label)
            if score > best_score:
                best_score = score
                best_repo = repo

        if best_repo is None:
            return None, likely_oss

        threshold = 4.2 if likely_oss else 6.2
        if best_score < threshold:
            return None, likely_oss

        pushed_at = (best_repo.get("pushed_at") or "")[:10]
        stars = int(best_repo.get("stargazers_count") or 0)
        return (
            GithubSignal(
                repo_full_name=best_repo.get("full_name") or "",
                stars=stars,
                pushed_at=pushed_at or "unknown",
                confidence=best_score,
            ),
            likely_oss,
        )

    @staticmethod
    def _source_is_trusted(source_domain: str, startup_host: str) -> bool:
        if not source_domain:
            return False
        if startup_host and (
            source_domain == startup_host
            or source_domain.endswith(f".{startup_host}")
        ):
            return True
        for trusted in TRUSTED_MARKET_DATA_DOMAINS:
            if source_domain == trusted or source_domain.endswith(f".{trusted}"):
                return True
        return False

    @staticmethod
    def _is_plausible_money_millions(
        amount_m: Optional[float], total_raised_m: Optional[float], is_valuation: bool
    ) -> bool:
        if amount_m is None:
            return False
        if amount_m <= 0:
            return False
        # Hard cap to avoid obviously wrong captures from snippets.
        if amount_m > (50000 if is_valuation else 5000):
            return False
        if total_raised_m and total_raised_m > 0:
            cap = total_raised_m * (80 if is_valuation else 25)
            floor = total_raised_m * (0.8 if is_valuation else 0.05)
            if amount_m > max(cap, 1000):
                return False
            if is_valuation and amount_m < floor:
                return False
        return True

    def _extract_funding_signal(
        self,
        results: List[Dict[str, str]],
        startup_host: str,
        total_raised_m: Optional[float],
    ) -> Dict[str, str]:
        funding_round = ""
        funding_amount = ""
        funding_source = ""
        valuation_amount = ""
        valuation_source = ""

        for item in results:
            text = f"{item.get('title', '')}. {item.get('snippet', '')}"
            lowered = text.lower()
            source = extract_domain_for_display(item.get("url", ""))
            if not self._source_is_trusted(source, startup_host):
                continue

            round_match = ROUND_RE.search(text)
            if not funding_round and round_match:
                funding_round = round_match.group(1).strip().title()
                funding_source = source

            if not funding_amount and any(
                token in lowered
                for token in ["raised", "funding", "round", "series", "secured"]
            ):
                amount_match = MONEY_RE.search(text)
                if amount_match:
                    candidate = amount_match.group(0).replace("  ", " ").strip()
                    candidate_m = parse_money_to_millions(candidate)
                    if self._is_plausible_money_millions(
                        candidate_m, total_raised_m, is_valuation=False
                    ):
                        funding_amount = candidate
                        if not funding_source:
                            funding_source = source

            if "valuation" in lowered or "valued" in lowered or "post-money" in lowered:
                tail = text
                start = 0
                for keyword in ["valuation", "valued", "post-money"]:
                    idx = lowered.find(keyword)
                    if idx >= 0:
                        start = idx
                        break
                tail = text[start:]
                val_match = MONEY_RE.search(tail)
                if val_match and not valuation_amount:
                    candidate = val_match.group(0).replace("  ", " ").strip()
                    candidate_m = parse_money_to_millions(candidate)
                    if self._is_plausible_money_millions(
                        candidate_m, total_raised_m, is_valuation=True
                    ):
                        valuation_amount = candidate
                        valuation_source = source

        return {
            "round": funding_round,
            "amount": funding_amount,
            "funding_source": funding_source,
            "valuation": valuation_amount,
            "valuation_source": valuation_source,
        }

    @staticmethod
    def _estimate_valuation_range(
        total_raised_m: Optional[float], employees: Optional[int]
    ) -> str:
        if total_raised_m is not None and total_raised_m > 0:
            if total_raised_m < 2:
                low_mult, high_mult = 8.0, 20.0
            elif total_raised_m < 8:
                low_mult, high_mult = 5.0, 12.0
            elif total_raised_m < 20:
                low_mult, high_mult = 4.0, 9.0
            elif total_raised_m < 50:
                low_mult, high_mult = 3.0, 7.0
            else:
                low_mult, high_mult = 2.5, 5.5

            if employees:
                if employees >= 120:
                    high_mult *= 1.2
                elif employees <= 20:
                    low_mult *= 0.9

            low = total_raised_m * low_mult
            high = total_raised_m * high_mult
            return f"{format_millions(low)}-{format_millions(high)} (estimate)"

        if employees:
            if employees >= 100:
                return "$120.0M-$400.0M (estimate, undisclosed funding profile)"
            if employees >= 40:
                return "$40.0M-$180.0M (estimate, undisclosed funding profile)"
            if employees >= 15:
                return "$15.0M-$80.0M (estimate, undisclosed funding profile)"
        return "Undisclosed"

    def funding_and_valuation_summary(
        self,
        startup_name: str,
        startup_host: str,
        search_results: List[Dict[str, str]],
        total_raised_m: Optional[float],
        employees: Optional[int],
    ) -> str:
        signal = self._extract_funding_signal(search_results, startup_host, total_raised_m)

        if signal["amount"]:
            round_label = signal["round"] or "Latest round"
            source = (
                f" ({signal['funding_source']} signal)"
                if signal["funding_source"]
                else ""
            )
            funding_text = f"{round_label}: {signal['amount']}{source}"
        elif total_raised_m is not None and total_raised_m > 0:
            funding_text = (
                f"Total raised disclosed: {format_millions(total_raised_m)} "
                "(latest round not clearly public)"
            )
        else:
            funding_text = "No reliable public latest-round amount detected"

        if signal["valuation"]:
            source = (
                f" ({signal['valuation_source']} signal)"
                if signal["valuation_source"]
                else ""
            )
            valuation_text = f"{signal['valuation']}{source}"
        else:
            valuation_text = self._estimate_valuation_range(total_raised_m, employees)

        return f"{funding_text}; Est./latest valuation: {valuation_text}"

    def market_sentiment_summary(
        self,
        search_results: List[Dict[str, str]],
        github_signal: Optional[GithubSignal],
    ) -> str:
        g2_rating: Optional[float] = None
        for item in search_results:
            text = f"{item.get('title', '')}. {item.get('snippet', '')}"
            if "g2" not in text.lower() and "g2.com" not in (item.get("url") or ""):
                continue
            match = G2_RATING_RE.search(text)
            if match:
                try:
                    g2_rating = float(match.group(1))
                    break
                except ValueError:
                    continue

        if g2_rating is not None:
            if g2_rating >= 4.5:
                tone = "very positive"
            elif g2_rating >= 4.0:
                tone = "positive"
            elif g2_rating >= 3.5:
                tone = "mixed-positive"
            else:
                tone = "mixed"
            return f"G2: {g2_rating:.1f}/5 ({tone})"

        stars = github_signal.stars if github_signal else 0
        if stars >= 10000:
            return f"Developer sentiment: very positive (OSS traction {stars:,} stars)"
        if stars >= 3000:
            return f"Developer sentiment: positive (OSS traction {stars:,} stars)"
        if stars >= 500:
            return f"Developer sentiment: generally positive (OSS traction {stars:,} stars)"
        if stars > 0:
            return f"Developer sentiment: early/niche but active ({stars:,} stars)"
        return "No strong public G2 signal; sentiment appears mixed or enterprise-led"

    @staticmethod
    def ai_native_competitors(name: str, description: str) -> str:
        text = f"{name} {description}".lower()

        if any(k in text for k in ["identity", "iam", "auth", "login", "permission"]):
            return "Descope; Clerk AI tooling"
        if any(
            k in text
            for k in ["testing", "regression", "qa", "test automation", "quality"]
        ):
            return "KushoAI; Momentic"
        if any(
            k in text
            for k in ["code review", "code quality", "static analysis", "sast", "lint"]
        ):
            return "CodeRabbit; Greptile"
        if any(
            k in text
            for k in [
                "security",
                "compliance",
                "vulnerability",
                "attack",
                "zero trust",
                "posture",
            ]
        ):
            return "Protect AI; Dropzone AI"
        if any(
            k in text
            for k in ["observability", "monitoring", "logs", "metrics", "telemetry", "apm"]
        ):
            return "Coroot AI workflows; Datadog Bits AI"
        if any(
            k in text
            for k in ["database", "sql", "query", "warehouse", "vector", "graph", "search engine"]
        ):
            return "MotherDuck + AI analyst workflows; Neon AI-native Postgres workflows"
        if any(k in text for k in ["kafka", "stream", "event"]):
            return "Confluent AI Assistant; Aiven AI copilots"
        if any(k in text for k in ["finops", "cost", "cloud expenses", "spend"]):
            return "CloudZero AI insights; Finout AI optimization"
        if any(
            k in text
            for k in [
                "api gateway",
                "api management",
                "integration",
                "feature flag",
                "notification",
            ]
        ):
            return "Postman AI Agent Builder; Speakeasy AI SDK workflows"
        if any(
            k in text
            for k in [
                "devops",
                "kubernetes",
                "infrastructure",
                "terraform",
                "platform engineering",
                "ci/cd",
                "deployment",
                "serverless",
                "container",
                "cloud",
            ]
        ):
            return "Kubiya; Harness AIDA"
        if any(k in text for k in ["collaboration", "documentation", "workflow", "project"]):
            return "Atlassian Rovo; Notion AI"
        return "Cognition Devin platform; Factory AI agents"

    def enrich_row(self, row: Dict[str, str]) -> Dict[str, str]:
        name = (row.get("Name") or "").strip()
        url = (row.get("URL") or "").strip()
        description = (row.get("Description") or "").strip()
        host = host_from_url(url)
        total_raised_m = safe_float(row.get("Total Raised, M$"))
        employees = safe_int(row.get("Employees"))

        gh_signal, likely_oss = self.github_signal(name, url, description)

        if gh_signal:
            gh_text = (
                f"{gh_signal.repo_full_name} | {gh_signal.stars:,} stars | "
                f"last commit {gh_signal.pushed_at}"
            )
        elif likely_oss:
            gh_text = "Likely OSS, but no primary repo confidently matched"
        else:
            gh_text = "N/A (primarily closed-source / managed service profile)"

        search_results = self.brave_search(
            f"{name} latest funding round valuation g2 developer reviews"
        )
        funding_text = self.funding_and_valuation_summary(
            name, host, search_results, total_raised_m, employees
        )
        sentiment_text = self.market_sentiment_summary(search_results, gh_signal)
        competitors_text = self.ai_native_competitors(name, description)

        return {
            "Startup": name,
            "Latest Funding & Valuation": funding_text,
            "GitHub/OSS Traction": gh_text,
            "AI-Native Competitors": competitors_text,
            "Market Sentiment": sentiment_text,
        }


def write_csv(path: Path, rows: List[Dict[str, str]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: List[Dict[str, str]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    headers = list(rows[0].keys())
    with path.open("w", encoding="utf-8") as f:
        f.write("| " + " | ".join(headers) + " |\n")
        f.write("|" + "|".join(["---"] * len(headers)) + "|\n")
        for row in rows:
            cells = []
            for h in headers:
                val = (row.get(h) or "").replace("|", "\\|")
                cells.append(val)
            f.write("| " + " | ".join(cells) + " |\n")


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_PATH}")

    with INPUT_PATH.open("r", encoding="utf-8", newline="") as f:
        source_rows = list(csv.DictReader(f))

    enricher = StartupEnricher()
    enriched_rows: List[Dict[str, str]] = []

    total = len(source_rows)
    for idx, row in enumerate(source_rows, start=1):
        name = row.get("Name") or f"row-{idx}"
        print(f"[{idx:>3}/{total}] Enriching: {name}")
        try:
            enriched_rows.append(enricher.enrich_row(row))
        except Exception as exc:  # pylint: disable=broad-except
            # Keep processing the full list even if one startup fails.
            enriched_rows.append(
                {
                    "Startup": name,
                    "Latest Funding & Valuation": f"Enrichment error: {exc}",
                    "GitHub/OSS Traction": "N/A",
                    "AI-Native Competitors": "N/A",
                    "Market Sentiment": "N/A",
                }
            )

    today = dt.date.today().isoformat()
    out_csv = OUTPUT_DIR / f"startup_market_enriched_{today}.csv"
    out_md = OUTPUT_DIR / f"startup_market_enriched_{today}.md"
    write_csv(out_csv, enriched_rows)
    write_markdown(out_md, enriched_rows)

    print(f"\nDone. Wrote {len(enriched_rows)} rows.")
    print(f"CSV: {out_csv}")
    print(f"MD:  {out_md}")


if __name__ == "__main__":
    main()
