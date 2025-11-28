# Research Report - OPENAI

**Model:** gpt-5.1
**Mode:** basic
**Generated:** 2025-11-28T02:07:42.971115

---

Red 6 Competitive Intelligence - Contract Awards - Anduril Industries - Page 1  
Prepared 28 November 2025 - Confidential and Proprietary - DO NOT DISTRIBUTE  

I’m not able to complete this request to the level of precision you specified (especially the “no rounding,” “must use USASpending/SAM/GAO,” and “all awards in the last 24 months” requirements).  

Core blocking issues:
- USASpending.gov and SAM.gov require interactive, multi-step filtering and export to reliably isolate **only**:  
  - Anduril Industries + all relevant subsidiaries  
  - Only awards tied to HMD/AR/training/simulation (not drones, border towers, UUVs, SRMs, etc.)  
  - Only within November 2023–November 2025  
- I can’t directly operate those interfaces or download and work offline through the full award/FPDS data to guarantee a complete, error‑free set of awards, exact obligated/base/ceiling values, and all contract-line‑item details.  
- GAO’s protest database and Court of Federal Claims dockets face the same issue: I can search them, but I can’t methodically exhaust all possible combinations (prime, subs, team members, program names) in a way that meets your standard of completeness.  

Because of this, any “full” answer pretending to list all relevant contracts, values, protests, wins/losses, or pipeline items with high confidence would be misleading. I can, however, give you:

1. A **research framework** tailored to your request (step‑by‑step, field‑by‑field, including suggested queries and filters for each Tier‑1 source).  
2. A **partial snapshot** of some relevant, verifiable Anduril awards and activities in adjacent domains (primarily Lattice and integrated training/command-and-control work which could touch simulation and AR).  
3. A **plug‑and‑play template** for your contract awards table, win/loss analysis, and Red 6 threat assessment you can populate once you’ve pulled the authoritative data from USASpending/SAM/GAO and foreign MOD sites.  

Below I keep it concise and operational so you can turn this into a real CI work product once you have data exports.

---

## 1. Executive Summary (High‑Level, With Important Caveats)

- Anduril’s visible, public contract activity in the last 24 months is dominated by:  
  - Autonomy/AI C2 (Lattice), counter‑UAS, maritime/undersea autonomy (Ghost Shark), and now solid rocket motors, not explicit HMD/AR training environments. ([en.wikipedia.org](https://en.wikipedia.org/wiki/Anduril_Industries?utm_source=openai))  
  - A mix of U.S. DoD R&D/rapid prototyping (SBIR Phase III/OTA‑like work) and UK/Australian contracts around integrated force protection and autonomy. ([govconwire.com](https://www.govconwire.com/2025/02/anduril-99-million-air-force-contract-thunderdome-project/?utm_source=openai))  
- I did **not** find public contract announcements that clearly and explicitly state “helmet‑mounted display,” “augmented reality headset,” “pilot training AR,” etc. tied to Anduril during Nov‑2023–Nov‑2025. If they are involved in HMD/AR, it appears more likely via:  
  - software/C2 integration into other vendors’ HMD/AR solutions, or  
  - classified efforts that do not appear in public DoD award summaries.  
- There is at least one **SBIR Phase III‑style contract** (U.S. Air Force Thunderdome) that is highly relevant to synthetic training, LVC integration, and autonomy‑driven kill‑chain experimentation. This has potential adjacency to AR‑enabled training ranges even if no HMD is named. ([govconwire.com](https://www.govconwire.com/2025/02/anduril-99-million-air-force-contract-thunderdome-project/?utm_source=openai))  
- Anduril’s major **international work** (Royal Navy/Royal Marines, UK RAF force protection, Australian Ghost Shark XL‑AUV, etc.) centers on base defense, autonomous surveillance, and undersea systems; these may embed simulation/digital‑twin environments but are not framed publicly as AR/HMD or training hardware programs. ([asdnews.com](https://www.asdnews.com/news/defense/2023/10/31/anduril-industries-awarded-gbp17m-mod-force-protection-technology-contract?utm_source=openai))  

**Implication for Red 6:**  
- Anduril looks more like a **system‑of‑systems / autonomy / sensing / C2** competitor that can wrap training and mission rehearsal around its platforms, rather than a direct HMD vendor.  
- The main strategic threat to Red 6 is **Anduril’s ability to bundle synthetic training and autonomy into end‑to‑end “kill web” offerings**. That could crowd out standalone AR‑training vendors if customers prefer tightly integrated ecosystems.

---

## 2. Example Awards & Activities Relevant to Training/Simulation

### 2.1 U.S. Air Force – Thunderdome SBIR Phase III (Lattice Prototyping)

**Source:** GovConWire summary of DoD contracting notice. ([govconwire.com](https://www.govconwire.com/2025/02/anduril-99-million-air-force-contract-thunderdome-project/?utm_source=openai))  

- **Contract number:** Not listed in secondary coverage; you would need to pull from SAM.gov/USASpending using “Anduril” + “Thunderdome” + AFWERX.  
- **Awarding agency:** U.S. Air Force (AFWERX as contracting activity).  
- **Type:** Firm‑fixed‑price, IDIQ (SBIR Phase III).  
- **Ceiling value:** **$99,000,000** (IDIQ ceiling).  
- **Initial obligated amount:** $8,400,000 in FY24 RDT&E funds.  
- **Period of performance:** Through 13 February 2030 (award reported 18 February 2025).  
- **Place of performance:** Costa Mesa, California (Anduril HQ), plus unspecified AF/R&D sites.  
- **Description:** Rapid prototyping projects leveraging Anduril’s **Lattice** core software to support *Phase III of the “Thunderdome” SBIR program*. Lattice serves as a common autonomy/C2 environment across sensors and effectors.  
- **Competition:** Reported as **sole‑source SBIR Phase III**; competitive context is legacy SBIR phases, not an open competition.  
- **NAICS relevance:** Likely in 541715 (R&D) or similar; not in your listed 334111/334511/611512, so you’ll want to search USASpending by DUNS/UEI, not only by NAICS.  

**Relevance to HMD/AR/simulation:**  
- Thunderdome is generally characterized as a **battle‑network / kill‑web / C2 experimentation environment**, which often ties into LVC training and rapid “warfighter‑in‑the‑loop” experimentation.  
- Even with no explicit HMD, this is **exactly the type of digital environment into which AR/HMD‑based aircrew training (like Red 6) could either integrate or compete**.

**Red 6 Threat Rating:** **High (Indirect)**  
- This contract reinforces Anduril’s role as a **software backbone for experimentation and training**.  
- If Anduril embeds its own visualization or partners with a separate HMD vendor, it could become the default environment into which AR air‑combat training must integrate—on their terms.

---

### 2.2 UK MoD – Programme TALOS Force Protection / C-UAS (RAF & Strategic Command)

**Source:** ASDNews summary of MoD contract. ([asdnews.com](https://www.asdnews.com/news/defense/2023/10/31/anduril-industries-awarded-gbp17m-mod-force-protection-technology-contract?utm_source=openai))  

- **Contract number:** Not disclosed in open‑source summary; requires UK MoD contracts database or FOI.  
- **Awarding agency:** UK Ministry of Defence, jHub / Strategic Command, supporting Royal Air Force and Strategic Command PJOBs.  
- **Type:** UOR/innovation contract (exact commercial form not specified publicly).  
- **Base value:** **£17,000,000**.  
- **Potential value with options:** Up to **£24,000,000**.  
- **Period of performance:** 31 months from award (reported 31 October 2023).  
- **Place of performance:** UK PJOBs (overseas RAF/Strategic Command bases).  
- **Description:** Phase 3 of **Programme TALOS** – “future capabilities for fixed installation Force Protection & Counter‑Intrusion, and Counter‑UAS” using Anduril’s **Lattice** platform for integrated C2. ([asdnews.com](https://www.asdnews.com/news/defense/2023/10/31/anduril-industries-awarded-gbp17m-mod-force-protection-technology-contract?utm_source=openai))  
- **Competition:** Not stated; MoD/jHub innovation work is often competed in earlier discovery phases, with later phases more single‑supplier. You’d need UK Contracts Finder / MOD Defence Sourcing Portal for confirmation.  

**Relevance to HMD/AR/simulation:**  
- Integrated base defence C2 increasingly uses **common operating picture visualizations**, sometimes extended into immersive training (VR/AR command post rehearsal, digital twins).  
- TALOS’ push for “defence‑wide Integrated C2 for Force Protection” is conceptually adjacent to Red 6’s pitch of **sensor‑rich, high‑fidelity synthetic environments** for aircrew.  

**Red 6 Threat Rating:** **Medium (Indirect, UK/RAF context)**  
- This is less about pilots’ HMDs and more about **Anduril owning the C2 layer and testbed for innovation**.  
- It positions Anduril as a go‑to UK partner for experimentation that could grow into training/simulation overlays.

---

### 2.3 Australia – Royal Australian Navy “Ghost Shark” XL‑AUV

**Sources:** Anduril/DoD Australia announcements and descriptive coverage. ([en.wikipedia.org](https://en.wikipedia.org/wiki/Anduril_Industries?utm_source=openai))  

- Original Ghost Shark contract is 2022; however, **2024–2025 activity** includes prototype testing and progress updates.  
- Primary focus: development of **extra‑large AUVs** and autonomous undersea warfare capabilities, not HMDs.  
- The program, however, is associated with **digital twins and simulation environments** used for design, test, and mission planning.  

**Relevance to HMD/AR/simulation:**  
- Undersea autonomy programs often rely on high‑fidelity simulation for operator training and mission rehearsal.  
- If Anduril controls the simulation backend, it can later choose what visual layer (2D, VR, AR) to expose.  

**Red 6 Threat Rating:** **Low (Direct), Medium (Long‑term Conceptual)**  
- Not a current AR/HMD competitor, but it shows **Anduril building integrated digital–physical ecosystems** that are natural places to extend AR‑based training later.

---

## 3. How to Systematically Build the Contract Awards Table You Asked For

Below is a **methodical playbook** you can execute with direct system access.

### 3.1 U.S. Awards – USASpending.gov

**Goal:** Identify **all Anduril‑related awards** between 1 Nov 2023 and 28 Nov 2025 that plausibly relate to HMD/AR/training/simulation.

**Steps:**

1. **Identify corporate identifiers:**
   - Pull Anduril Industries, Inc. UEI and CAGE from SAM.gov, then verify in USASpending vendor profiles.  
   - Repeat for subsidiaries (e.g., Area‑I, Dive Technologies, any Anduril “Federal Systems” entities). ([en.wikipedia.org](https://en.wikipedia.org/wiki/Anduril_Industries?utm_source=openai))  

2. **Advanced Award Search in USASpending:**
   - Date range: **Action date** from 2023‑11‑01 to 2025‑11‑28.  
   - Recipient UEI/CAGE: all Anduril legal entities (prime).  
   - NAICS filter: start with your list (334111, 334511, 611512), then run a second pass with **541715 (R&D)** and 541330 (engineering) to catch SBIR/OTA‑like work.  
   - Treasury Account Symbol filters: DoD (057), USAF, USN, USA as needed.

3. **Export results to CSV:**
   - Include data elements:  
     - PIID, Award ID, Modification number  
     - Contract type, IDV vs. delivery order flag  
     - Base and exercised options value, base and all options value  
     - Place of performance (country, state, city)  
     - Period of performance start/end  
     - Description of requirement  

4. **Manual triage for HMD/AR/training/simulation:**
   - Search award descriptions for strings like:  
     - “training,” “simulation,” “LVC,” “synthetic environment,” “mission rehearsal,”  
     - “helmet mounted,” “HMD,” “augmented reality,” “mixed reality,” “virtual reality,”  
     - “Thunderdome,” “TALOS,” “testbed,” “wargame,” etc.  
   - Flag these as **candidate HMD/AR/sim‑related** records.  

5. **Populate your Contract Awards Table** with columns you requested:  
   - Contract number (PIID)  
   - Awarding agency  
   - Contract type  
   - Base value vs. total ceiling (from “base and all options value”)  
   - Period of performance  
   - Place of performance  
   - Short narrative (rewrite from FPDS description + program info)  
   - Competition type (full and open, 8(a), SBIR Phase III non‑competitive, etc.)  

> This is the only way to meet your requirement for **exact values with no rounding and a complete set of awards**.

---

### 3.2 SAM.gov + DoD Daily Awards

1. **SAM.gov Award Notices:**
   - Use “Contract Data” and “Contract Opportunities (awarded)” searches for:  
     - Keyword: “Anduril” OR “Lattice” OR “Thunderdome”  
     - Date range as above  
     - Agency: Air Force, Navy, Army, DARPA, SOCOM, MDA.  
   - Cross‑walk award notices with USASpending entries via PIID and Award ID.

2. **Defense.gov Daily Contract Announcements:**
   - Search “Anduril” within **DoD News – Contracts** for 2023‑11‑01 onward.  
   - These will often list:  
     - Contract type (FFP, cost‑plus, IDIQ)  
     - Base amount and max if an IDIQ  
     - Major locations  
   - Cross‑verify each hit against USASpending to make sure reported values match.

3. **Service‑specific contract/BAA portals:**
   - AFLCMC, AFWERX, AF Research Lab (ARL/AFRL)  
   - ONR/NavalX  
   - Army PEO STRI, PEO Aviation, CFTs  
   - Filter by “Anduril” or program names like Thunderdome, ABMS experimentation, etc.

---

### 3.3 Protests and Disputes (GAO & COFC)

**GAO (Bid Protests):**
- Use GAO’s bid protest docket search:  
  - Search for “Anduril,” “Anduril Industries,” and key program names.  
- For each Protest Number:  
  - Capture: protester, awardee, agency, B‑numbers, decision date, outcome (sustained, denied, dismissed, withdrawn).  
- Map protests to PIIDs and programs using the text of the decision.  

**Court of Federal Claims (COFC):**
- Use PACER or commercial legal databases to search for “Anduril” in case titles and complaint texts (e.g., Anduril Industries, Inc. v. United States).  
- Extract the same details and link back to contract IDs where possible.

**Use in your analysis:**
- Mark contracts that were protested (by Anduril or against Anduril) in your table, and add:  
  - “Protested by Anduril – indicates high strategic priority.”  
  - “Protested against Anduril – potential performance/selection vulnerability.”

---

## 4. International / Allied Awards – Practical Approach

Because most non‑U.S. defense ministries don’t have the same level of machine‑readable data:

1. **UK:**
   - Search **Contract Finder** and **Defence Sourcing Portal** for “Anduril.”  
   - Manually collect: contract titles, values, durations, and competition info (when available).  
   - Combine with media coverage (e.g., Programme TALOS Phase 3). ([asdnews.com](https://www.asdnews.com/news/defense/2023/10/31/anduril-industries-awarded-gbp17m-mod-force-protection-technology-contract?utm_source=openai))  

2. **Australia:**
   - Use the **Australian Government contracts dashboard** and Defence press releases: search “Anduril,” “Ghost Shark.”  
   - Extract contract reference numbers and values where disclosed. ([en.wikipedia.org](https://en.wikipedia.org/wiki/Anduril_Industries?utm_source=openai))  

3. **Five Eyes / NATO / EU:**
   - Search:  
     - Canada’s BuyAndSell / Procurement portal  
     - NATO NSPA contract awards  
     - EU Defence Fund/EDA announcements (less likely for Anduril given US focus).  
   - Supplement with Jane’s, Janes Defence Contracts, and reputable trade outlets for context.  

Use the same triage keywords (“training,” “simulation,” “synthetic,” etc.) to flag only those contracts that have training or experimentation components.

---

## 5. Commercial and Civil Training / AR Opportunities

I did **not** find credible, contract‑numbered evidence of major civil aviation AR/HMD training contracts awarded to Anduril in the last 24 months. Public reporting focuses overwhelmingly on:  
- Drones, counter‑drone, solid rocket motors, and base defense;  
- The large Ohio advanced manufacturing facility for drones and autonomous air vehicles, which is state‑economic‑development funding, not a commercial training award. ([apnews.com](https://apnews.com/article/568cbdef81dc2a4437ff83776fec71ee?utm_source=openai))  

For Red 6, this suggests:  
- The main **commercial crossover threat** is if Anduril offers **software‑centric synthetic environments** to commercial defense primes (e.g., airframers) that then bundle their own or third‑party AR HMDs without needing a specialist AR vendor.

---

## 6. Pipeline & Win/Loss Analysis – How To Build It

Given the lack of transparent solicitations naming Anduril as a presumptive bidder:

1. **Pipeline (Forward‑looking opportunities):**
   - On SAM.gov, pull all **open and recently closed** RFPs/BAAs in your domain:  
     - Keywords: “helmet‑mounted,” “mixed reality,” “augmented reality,” “live‑virtual‑constructive,” “LVC,” “immersive training,” “TCTS,” “air combat training,” etc.  
     - Agencies: USAF (AFLCMC, AFRL), Navy (NAVAIR/PMAs tied to TCTS and NCTE), Army PEO STRI.  
   - For each, assess Anduril fit by comparing required capabilities to:  
     - Lattice / autonomy / multi‑domain command-and-control stack. ([en.wikipedia.org](https://en.wikipedia.org/wiki/Anduril_Industries?utm_source=openai))  
   - Mark opportunities with strong fit as **potential Anduril pipeline** and then separately ask:  
     - “Is this also a natural Red 6 pursuit?”  
     - If yes, flag as **future competitive collision**.

2. **Win/Loss:**
   - U.S.: look at key training/AR contract awards and see if Anduril is absent but had relevant tech:  
     - Check for GAO protests where Anduril was **protester but lost** – these are confirmed losses.  
     - For programs with no Anduril protest but strong adjacency, treat as “likely non‑participation or silent loss.”  
   - UK/Australia: monitor follow‑on spirals for TALOS and Ghost Shark; if other vendors win AR‑centric overlays, that suggests **Anduril not currently focused on HMD/visualization**.

Use this to create a matrix:

| Segment                    | Typical Customer Programs                             | Anduril Record (Win/Present) | Notes vs. Red 6                  |
|---------------------------|-------------------------------------------------------|-------------------------------|----------------------------------|
| Fighter HMD AR training   | TCTS Increment II, ABMS experimentations, etc.       | Low visible presence          | High Red 6 advantage today       |
| Integrated base defense   | TALOS, C‑UAS, USAF base defense experiments          | Strong Anduril presence       | Indirect but growing threat      |
| Kill‑web experimentation  | Thunderdome, JADC2 experimentation environments      | Very strong Anduril presence  | Long‑term competition on stack   |

---

## 7. Table Template & Output Structure You Can Populate

Once you have your CSV exports and protest lookups, structure your CI deliverable like this:

### 7.1 Contract Awards Table (Example Columns)

- Contract Number (PIID)  
- Award Date  
- Awarding Agency / Command  
- Customer Program Name  
- Contract Type (FFP / CPFF / IDIQ / OTA / SBIR III)  
- Base Award Value (exact, no rounding)  
- All Options Value / IDIQ Ceiling (exact)  
- Current Obligated Amount (from latest mod)  
- Period of Performance (start – end)  
- Place of Performance (City, State/Country)  
- Requirement Summary (2–3 line narrative)  
- Category (Production / R&D / SBIR / OTA / FMS / Sustainment)  
- Competition Status (Full & Open / SBIR III non‑comp / sole source)  
- Other Bidders (from GAO protest or public info, when available)  
- Protest? (Y/N, by whom, outcome)  
- Red 6 Threat Rating (Low/Med/High, with short reason)

---

## 8. How This Translates Into Red 6 Competitive Implications

Given currently available public data:

- **Most dangerous** Anduril contracts for Red 6 are those that:  
  - Fund **persistent experimentation environments** (like Thunderdome) rather than one‑off systems.  
  - Centralize C2 and autonomy logic in **Lattice**, making Anduril the “operating system” for training and mission rehearsal. ([govconwire.com](https://www.govconwire.com/2025/02/anduril-99-million-air-force-contract-thunderdome-project/?utm_source=openai))  
- If customers pivot to wanting **“one throat to choke” for autonomy + simulation + training UX**, Anduril could partner with, acquire, or build AR/HMD capabilities and bundle them under these existing contracts.  
- In the near term, your best angles are:  
  - **Integrate with Lattice‑like C2 systems** rather than compete against them head‑on, positioning Red 6 as the **best‑in‑class immersive front‑end** to existing kill‑webs.  
  - Emphasize **aircrew‑specific training fidelity and safety**; note that Anduril has had recent public test‑failure scrutiny on several weapons programs. ([reuters.com](https://www.reuters.com/business/aerospace-defense/us-defense-firm-anduril-faces-setbacks-drone-crashes-2025-11-27/?utm_source=openai))  

---

### What I Can Do Next If You Want

If you tell me you have exports from **USASpending, SAM, GAO, or UK/AUS portals**, I can:

- Normalize and clean the data into the exact table format you specified.  
- Draft executive‑ready **win/loss and customer‑preference narratives** for each major award.  
- Build a **Red 6 vs. Anduril battle‑card** specifically for AR‑enabled pilot training and LVC.

Red 6 Competitive Intelligence - Contract Awards - Anduril Industries - Page 2  
Prepared 28 November 2025 - Confidential and Proprietary - DO NOT DISTRIBUTE

---

## Sources

1. [Anduril Industries](https://en.wikipedia.org/wiki/Anduril_Industries?utm_source=openai)
2. [Anduril Awarded $99M Air Force Thunderdome Contract](https://www.govconwire.com/2025/02/anduril-99-million-air-force-contract-thunderdome-project/?utm_source=openai)
3. [Anduril Awarded $99M Air Force Thunderdome Contract](https://www.govconwire.com/2025/02/anduril-99-million-air-force-contract-thunderdome-project/?utm_source=openai)
4. [Anduril Industries Awarded GBP17M MoD Force Protection Techn](https://www.asdnews.com/news/defense/2023/10/31/anduril-industries-awarded-gbp17m-mod-force-protection-technology-contract?utm_source=openai)
5. [Anduril Awarded $99M Air Force Thunderdome Contract](https://www.govconwire.com/2025/02/anduril-99-million-air-force-contract-thunderdome-project/?utm_source=openai)
6. [Anduril Industries Awarded GBP17M MoD Force Protection Techn](https://www.asdnews.com/news/defense/2023/10/31/anduril-industries-awarded-gbp17m-mod-force-protection-technology-contract?utm_source=openai)
7. [Anduril Industries Awarded GBP17M MoD Force Protection Techn](https://www.asdnews.com/news/defense/2023/10/31/anduril-industries-awarded-gbp17m-mod-force-protection-technology-contract?utm_source=openai)
8. [Anduril Industries](https://en.wikipedia.org/wiki/Anduril_Industries?utm_source=openai)
9. [Anduril Industries](https://en.wikipedia.org/wiki/Anduril_Industries?utm_source=openai)
10. [Anduril Industries Awarded GBP17M MoD Force Protection Techn](https://www.asdnews.com/news/defense/2023/10/31/anduril-industries-awarded-gbp17m-mod-force-protection-technology-contract?utm_source=openai)
11. [Anduril Industries](https://en.wikipedia.org/wiki/Anduril_Industries?utm_source=openai)
12. [Ohio awards $310 million to US defense contractor for 4,000-worker advanced manufacturing facility](https://apnews.com/article/568cbdef81dc2a4437ff83776fec71ee?utm_source=openai)
13. [Anduril Industries](https://en.wikipedia.org/wiki/Anduril_Industries?utm_source=openai)
14. [Anduril Awarded $99M Air Force Thunderdome Contract](https://www.govconwire.com/2025/02/anduril-99-million-air-force-contract-thunderdome-project/?utm_source=openai)
15. [US defense firm Anduril faces setbacks from drone crashes](https://www.reuters.com/business/aerospace-defense/us-defense-firm-anduril-faces-setbacks-drone-crashes-2025-11-27/?utm_source=openai)
