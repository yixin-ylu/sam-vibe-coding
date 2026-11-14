"""
Generate the synthetic case dataset used by every SAM demo.

CASE: Smiley (a FICTIONAL AI-tutoring startup) runs "Learn Smarter", a 12-week,
$1.2M back-to-school campaign (Aug 3 - Oct 25, 2026) to launch Smiley Pro.

  Audiences : Students (B2C users), Parents (B2C payers), Educators (B2B school licenses)
  Channels  : TikTok, Instagram, YouTube, LinkedIn, organic + paid
  Funnel    : impressions -> clicks -> free trials -> paid subscribers
              (LinkedIn also -> school demo requests)

Patterns hidden in the data for students to discover:
  1. TikTok has the cheapest TRIALS but the most expensive CUSTOMERS
     (students try, parents pay): CPA and CAC rank channels differently.
  2. Creator/UGC content wins on TikTok and Instagram; testimonials win with parents;
     thought leadership drives school demo requests on LinkedIn; promos flop on LinkedIn.
  3. Week 7 (Sep 14): a viral post alleges Smiley trains its AI on student data.
     Privacy complaints spike, parent conversions collapse, then recover after the
     "Trust & privacy" content the team launches in week 8.
  4. From week 9 the team scales TikTok spend about 60% over plan: CPM rises, CTR
     falls (diminishing returns) and the campaign overspends.
  5. An A/B test of two TikTok ad hooks (weeks 4-5): B gets more clicks, A gets more
     trials per click, and B's claim may be an unsubstantiated efficacy claim.

Everything is synthetic: no real company, people or personal data.

Run:  python data/generate_sample_data.py
"""
from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

SEED = 2026
OUT = Path(__file__).resolve().parent
START = datetime(2026, 8, 3)          # Monday, week 1
WEEKS = 12
CRISIS_WEEK = 7
REVENUE_PER_PAID = 96.0               # avg first-year revenue per subscriber (USD)
PIPELINE_PER_DEMO = 1500.0            # expected value of a school demo request: ~10% close x $15k license

PLATFORMS = {
    # followers, weekly growth, segment mix, CPM $, base CTR, click->trial, base engagement rate
    "TikTok":    dict(followers=12000, growth=0.060, seg={"Students": .85, "Parents": .15},
                      cpm=9.0,  ctr=.0110, c2t=.070, eng=.055),
    "Instagram": dict(followers=18000, growth=0.030, seg={"Students": .50, "Parents": .50},
                      cpm=11.0, ctr=.0090, c2t=.060, eng=.035),
    "YouTube":   dict(followers=6000,  growth=0.040, seg={"Students": .55, "Parents": .45},
                      cpm=14.0, ctr=.0070, c2t=.090, eng=.025),
    "LinkedIn":  dict(followers=5000,  growth=0.025, seg={"Educators": 1.0},
                      cpm=45.0, ctr=.0055, c2t=.020, eng=.020),
}
WEEKLY_BUDGET = {"TikTok": 35000, "Instagram": 30000, "YouTube": 20000, "LinkedIn": 15000}
TRIAL_TO_PAID = {"Students": .05, "Parents": .22, "Educators": .08}
DEMO_RATE = .040                      # LinkedIn clicks -> school demo requests

FORMATS = {"TikTok": ["video"], "YouTube": ["video"],
           "Instagram": ["video", "carousel", "image"],
           "LinkedIn": ["text", "image", "video", "carousel"]}
FORMAT_ENG = {"video": 1.25, "carousel": 1.10, "image": 0.90, "text": 0.75}

PILLARS = {
    # pillar: (CTR mult, engagement mult, conversion mult)
    "Product demo":       (1.00, 0.90, 1.00),
    "Testimonial":        (1.10, 1.10, 1.10),
    "Study tips":         (0.80, 1.35, 0.70),
    "Creator/UGC":        (1.35, 1.50, 1.05),
    "Promo/discount":     (1.25, 0.80, 1.20),
    "Thought leadership": (1.00, 0.75, 1.00),
    "Trust & privacy":    (0.90, 0.90, 1.00),
}
CAPTIONS = {
    "Product demo": ["See how Smiley explains calculus step by step",
                     "60 seconds: Smiley turns your notes into a practice quiz",
                     "Stuck at 11pm? Ask Smiley, your AI study partner"],
    "Testimonial": ["\"My son finally likes chemistry\": a parent's story",
                    "How Maya went from cramming to confident with Smiley",
                    "A teacher on what changed after one semester with Smiley"],
    "Study tips": ["3 science-backed ways to remember more before exams",
                   "The 25-minute study method that actually works",
                   "How to turn a syllabus into a weekly plan"],
    "Creator/UGC": ["We gave 5 college creators Smiley for finals week",
                    "Creator challenge: study with me + Smiley",
                    "POV: your AI tutor won't let you skip the hard part"],
    "Promo/discount": ["Back-to-school: 30% off Smiley Pro annual",
                       "Free 14-day Pro trial ends Sunday",
                       "Student plan: first month $1"],
    "Thought leadership": ["What 2,000 teachers told us about AI in the classroom",
                           "Webinar: responsible AI tutoring in K-12",
                           "AI should explain, not answer: our pedagogy principles"],
    "Trust & privacy": ["Your data is yours: how Smiley protects student privacy",
                        "We never train our AI on student work. Here is the proof.",
                        "Live Q&A with our Chief Privacy Officer"],
}

COMMENT_TOPICS = {
    # topic: list of (text, sentiment)
    "praise": [("This app is amazing, my grades improved", "pos"),
               ("Love how it explains instead of just giving answers", "pos"),
               ("Best study tool I have used, worth it", "pos"),
               ("My daughter loves it, great support team", "pos")],
    "pricing": [("Too expensive for students", "neg"),
                ("Why is the annual plan so expensive?", "neg"),
                ("The discount is a great deal", "pos"),
                ("Is there a family plan?", "neu")],
    "privacy": [("Are you training your AI on my kid's homework? Not ok", "neg"),
                ("Deleting the app until you explain what you do with student data", "neg"),
                ("Who can see my child's data?", "neu"),
                ("Thanks for the clear privacy update, that helps", "pos")],
    "efficacy": [("Does it actually improve test scores? Show the evidence", "neu"),
                 ("Helped me pass my stats exam", "pos"),
                 ("Did not help me much, the explanations are too long", "neg")],
    "cheating": [("Isn't this just a cheating tool?", "neg"),
                 ("Teachers will hate this, students will just copy", "neg"),
                 ("Good that it refuses to just give answers", "pos")],
    "bugs": [("App keeps crashing on Android", "neg"),
             ("Login is broken again", "neg"),
             ("The math input is buggy and slow", "neg")],
    "question": [("Does it work for AP Biology?", "neu"),
                 ("Can schools get a group license?", "neu"),
                 ("Is it available in Spanish?", "neu")],
}
TOPIC_MIX = {
    "Students":  {"praise": .38, "pricing": .16, "privacy": .03, "efficacy": .10, "cheating": .08, "bugs": .15, "question": .10},
    "Parents":   {"praise": .30, "pricing": .18, "privacy": .12, "efficacy": .16, "cheating": .08, "bugs": .04, "question": .12},
    "Educators": {"praise": .28, "pricing": .04, "privacy": .14, "efficacy": .20, "cheating": .14, "bugs": .02, "question": .18},
}


def weighted(rng: random.Random, d: dict) -> str:
    return rng.choices(list(d), weights=list(d.values()))[0]


def hour_bonus(h: int) -> float:
    return 1.25 if 19 <= h <= 22 else 1.10 if 12 <= h <= 13 else 0.80 if h < 9 else 1.0


def main() -> None:
    rng = random.Random(SEED)
    posts, comments, plan = [], [], []
    pid, cid = 5000, 90000

    for platform, p in PLATFORMS.items():
        for w in range(1, WEEKS + 1):
            followers = int(p["followers"] * (1 + p["growth"]) ** (w - 1))
            budget = WEEKLY_BUDGET[platform]
            plan.append({"week": w, "platform": platform, "planned_spend_usd": budget})
            # actual weekly spend: TikTok scaled up from week 9 (the team chased cheap trials)
            scale = 1.6 if (platform == "TikTok" and w >= 9) else rng.uniform(0.92, 1.08)
            week_spend = budget * scale
            saturation = (week_spend / budget) ** 0.6      # CPM up, CTR down when over plan
            n_paid = rng.randint(2, 3)
            n_org = rng.randint(3, 4)
            paid_split = [rng.uniform(0.7, 1.3) for _ in range(n_paid)]
            paid_split = [x / sum(paid_split) for x in paid_split]

            for k in range(n_paid + n_org):
                paid = k < n_paid
                pid += 1
                seg = weighted(rng, p["seg"])
                pillar_pool = [x for x in PILLARS if x != "Trust & privacy" or w >= CRISIS_WEEK + 1]
                if platform == "LinkedIn":
                    pillar = rng.choice(["Thought leadership"] * 3 + ["Product demo", "Testimonial",
                                         "Promo/discount"] + (["Trust & privacy"] if w > CRISIS_WEEK else []))
                elif w > CRISIS_WEEK and seg == "Parents" and rng.random() < 0.35:
                    pillar = "Trust & privacy"
                else:
                    pillar = rng.choice([x for x in pillar_pool if x != "Thought leadership"])
                fmt = rng.choice(FORMATS[platform])
                hour = rng.choice([7, 8, 12, 13, 16, 17, 19, 20, 21, 22])
                ts = START + timedelta(weeks=w - 1, days=rng.randint(0, 6), hours=hour,
                                       minutes=rng.randint(0, 59))
                ctr_m, eng_m, conv_m = PILLARS[pillar]
                if pillar == "Creator/UGC" and platform in ("TikTok", "Instagram"):
                    ctr_m, eng_m = ctr_m * 1.15, eng_m * 1.15
                if pillar == "Testimonial" and seg == "Parents":
                    conv_m *= 1.30
                if pillar == "Promo/discount" and platform == "LinkedIn":
                    ctr_m, conv_m = ctr_m * 0.45, conv_m * 0.4

                # crisis effect on trust-sensitive segments
                crisis = 1.0
                if seg in ("Parents", "Educators"):
                    crisis = {CRISIS_WEEK: 0.50, CRISIS_WEEK + 1: 0.78}.get(w, 1.0)
                    if pillar == "Trust & privacy":
                        crisis = min(1.0, crisis * 1.35)

                if paid:
                    spend = round(week_spend * paid_split[k], 2)
                    cpm = p["cpm"] * saturation * rng.uniform(0.9, 1.1)
                    impressions = int(spend / cpm * 1000)
                    ctr = p["ctr"] * ctr_m / saturation ** 0.5 * hour_bonus(hour) * rng.uniform(0.85, 1.15)
                    eng = p["eng"] * eng_m * FORMAT_ENG[fmt] * 0.45
                else:
                    spend = 0.0
                    impressions = int(followers * rng.uniform(0.25, 0.9) * eng_m * hour_bonus(hour))
                    ctr = p["ctr"] * 0.6 * ctr_m * rng.uniform(0.8, 1.2)
                    eng = p["eng"] * eng_m * FORMAT_ENG[fmt] * hour_bonus(hour) * rng.uniform(0.8, 1.2)

                clicks = int(impressions * ctr)
                trials = int(round(clicks * p["c2t"] * conv_m * crisis * rng.uniform(0.85, 1.15)))
                paid_conv = int(round(trials * TRIAL_TO_PAID[seg] * conv_m * crisis * rng.uniform(0.8, 1.2)))
                demos = int(round(clicks * DEMO_RATE * conv_m * crisis
                                  * (1.6 if pillar == "Thought leadership" else 1.0)
                                  * rng.uniform(0.8, 1.2))) if platform == "LinkedIn" else 0
                interactions = int(impressions * eng)
                n_comments = int(interactions * rng.uniform(0.04, 0.10))
                if w == CRISIS_WEEK and seg in ("Parents", "Educators"):
                    n_comments = int(n_comments * 2.5)
                likes = int(interactions * rng.uniform(0.70, 0.82))
                shares = max(0, interactions - likes - n_comments)

                posts.append({
                    "post_id": pid, "posted_at": ts.isoformat(timespec="minutes"), "week": w,
                    "platform": platform, "segment": seg, "pillar": pillar, "format": fmt,
                    "paid": int(paid), "spend_usd": spend, "impressions": impressions,
                    "clicks": clicks, "likes": likes, "comments": n_comments, "shares": shares,
                    "video_views": int(impressions * rng.uniform(0.45, 0.7)) if fmt == "video" else 0,
                    "trials": trials, "paid_conversions": paid_conv, "demo_requests": demos,
                    "revenue_usd": round(paid_conv * REVENUE_PER_PAID, 2),
                    "pipeline_usd": round(demos * PIPELINE_PER_DEMO, 2), "followers": followers,
                    "caption": rng.choice(CAPTIONS[pillar]),
                })

                # sample up to 8 comments per post
                mix = dict(TOPIC_MIX[seg])
                if w == CRISIS_WEEK:
                    mix["privacy"] *= 12 if seg != "Students" else 5
                elif w == CRISIS_WEEK + 1:
                    mix["privacy"] *= 3
                for _ in range(min(n_comments, 8)):
                    cid += 1
                    topic = weighted(rng, mix)
                    options = COMMENT_TOPICS[topic]
                    if topic == "privacy" and w < CRISIS_WEEK + 1:
                        options = options[:3]        # the reassuring reply only appears after the response
                    text, _ = rng.choice(options)
                    comments.append({
                        "comment_id": cid, "post_id": pid, "platform": platform, "segment": seg,
                        "commented_at": (ts + timedelta(minutes=rng.randint(5, 900))).isoformat(timespec="minutes"),
                        "text": text,
                    })

    # A/B test: two TikTok ad hooks, 14 days, equal budget
    ab = []
    for day in range(14):
        date = (START + timedelta(weeks=3, days=day)).date().isoformat()
        for variant, hook, ctr, c2t in (("A", "Save 5 hours of homework a week", .0110, .074),
                                        ("B", "Go from a B to an A this semester", .0123, .061)):
            imp = int(rng.gauss(42000, 3000))
            clicks = sum(1 for _ in range(imp) if rng.random() < ctr)
            trials = sum(1 for _ in range(clicks) if rng.random() < c2t)
            ab.append({"date": date, "variant": variant, "hook": hook, "impressions": imp,
                       "clicks": clicks, "trials": trials})

    posts.sort(key=lambda r: r["posted_at"])
    for name, rows in (("campaign_posts.csv", posts), ("campaign_comments.csv", comments),
                       ("budget_plan.csv", plan), ("ab_test.csv", ab)):
        with open(OUT / name, "w", newline="", encoding="utf-8") as f:
            wr = csv.DictWriter(f, fieldnames=list(rows[0]))
            wr.writeheader()
            wr.writerows(rows)
        print(f"wrote {len(rows):>5} rows -> data/{name}")


if __name__ == "__main__":
    main()
