# Shemoel Figma-import package

Each `.md` in this folder is a per-page narrative script for the Jayasom website.
Use them with your Claude / Figma workflow to assemble wireframes.

## How to use

1. Pick the page you're building (e.g. `01_homepage.md`).
2. Copy the entire file contents.
3. Paste into your Claude alongside this prompt:

   ```
   You are a senior product designer building a Figma wireframe for a luxury
   wellness website. The script below is the canonical content for one page —
   modules in render order, H1/Sub/Body/CTA structure preserved.

   Build a Figma frame for this page following these rules:
   - Desktop frame: 1440 width
   - Mobile frame: 375 width
   - One module per section, in the order listed
   - Use Jayasom brand colours (legacy purple #3E296B + neutrals)
   - Typography: Poppins SemiBold for headings, Poppins Light for body
   - Each {TBC} placeholder = leave a styled grey block + inline note
   - Module flag 'NEW: module' = the module needs a fresh wireframe
   - Module flag 'NEW: append element' = add the named element to the existing module
   - Module flag 'NEW: page' = the whole page is new on staging
   - Module flag 'EXISTING' or absent = wireframe matches the live module structure
   ```

4. The output should be a Figma-ready frame description; iterate as needed.

## Pages in this package

- `01_homepage.md` — Homepage
- `02_about_us.md` — About Us
- `03_wellness_landing.md` — Wellness
- `04_wellness_residences.md` — Wellness Residences
- `05_find_your_retreat.md` — Find Your Retreat
- `06_footer.md` — Footer
- `07_as_a_pair.md` — As a Pair
- `08_as_a_woman.md` — As a Woman
- `09_as_a_family.md` — As a Family
- `10_as_a_leader.md` — As a Leader
- `11_as_a_flow.md` — As a Flow
- `12_as_a_feather.md` — As a Feather
- `13_our_experts_listing.md` — Our Experts & Specialists
- `14_specialists_details.md` — Specialists Details
- `15_sp01_karen_campbell.md` — Sp01 — Karen Campbell
- `16_sp02_sascha_hemmann.md` — Sp02 — Sascha Hemmann
- `17_sp03_basel_shammout.md` — Sp03 — Basel Shammout
- `18_sp04_elodie_lefebvre.md` — Sp04 — Elodie Lefebvre
- `19_sp05_carol_el_hadi.md` — Sp05 — Carol El Hadi
- `20_sp06_lujain_abdullah_alhussan.md` — Sp06 — Lujain Abdullah AlHussan
- `21_sp07_vazeeq_madhar.md` — Sp07 — Vazeeq Madhar
- `22_sp08_eman_alsayoud.md` — Sp08 — Eman Alsayoud
- `23_sp09_mohammad_almslmany.md` — Sp09 — Mohammad Almslmany
- `24_sp10_amanda_hanna.md` — Sp10 — Amanda Hanna
- `25_treatments_listing.md` — Treatments
- `26_tx01_jayasom_signature.md` — Tx01 — Jayasom Signature
- `27_tx02_shirodhara.md` — Tx02 — Shirodhara
- `28_tx03_marma_point_therapy.md` — Tx03 — Marma Point Therapy
- `29_tx04_pinda_sweda.md` — Tx04 — Pinda Sweda
- `30_tx05_watsu.md` — Tx05 — Watsu
- `31_tx06_sound_healing.md` — Tx06 — Sound Healing
- `32_tx07_floatation_therapy.md` — Tx07 — Floatation Therapy
- `33_tx08_crystal_aroma_massage.md` — Tx08 — Crystal Aroma Massage
- `34_tx09_qalbain_two_hearts.md` — Tx09 — QALBAIN Two Hearts
- `35_tx10_ulfa_ritual.md` — Tx10 — Ulfa Ritual
- `36_tx11_vagus_nerve_ritual.md` — Tx11 — Vagus Nerve Ritual
- `37_tx12_hijama.md` — Tx12 — Hijama
- `38_tx13_hydrafacial_platinum.md` — Tx13 — Hydrafacial Platinum
- `39_tx14_detox_balneotherapy.md` — Tx14 — Detox Balneotherapy
- `40_tx15_reiki_taqa.md` — Tx15 — Reiki Taqa
- `41_individual_wellness.md` — Individual Wellness
- `42_wellbeing_spaces.md` — Wellbeing Spaces
- `43_culinary_nourishment.md` — Culinary Nourishment
- `44_group_activities.md` — Group Activities
- `45_activities_details.md` — Activities Details
- `46_retreats_and_programmes.md` — Retreats And Programmes
- `47_residential_community.md` — Residential Community
- `48_amaala_residences.md` — AMAALA Residences
- `49_rooms_and_villas.md` — Rooms & Villas
- `50_rooms_and_villas_details.md` — Rooms & Villas Details
- `51_rv_2br_villa.md` — R&V — 2BR Villa
- `52_rv_3br_villa.md` — R&V — 3BR Villa
- `53_rv_4br_villa.md` — R&V — 4BR Villa
- `54_rv_5br_jayela_residence.md` — R&V — 5BR Jayela Residence
- `55_view_residency.md` — View Residency
- `56_families_shared_wellbeing.md` — Families & Shared Wellbeing
- `57_insights.md` — Insights
- `58_journals_and_stories.md` — Journals & Stories
- `59_view_insight.md` — View Insight
- `60_news.md` — News
- `61_careers.md` — Careers
- `62_contact.md` — Contact

## Notes

- `{TBC}` markers are pending Karen + Carol decisions; render as styled placeholders.
- Verbatim canonical client copy is preserved word-for-word — do not paraphrase.
- Module render order in the script = expected scroll order on the page.
- Voice register notes inform the Figma copy treatment (formal vs warm vs editorial).

## Excluded pages

- 5 held Coming Soon sheets (Destinations / AMAALA Destination / Day at AMAALA / Retreats Old / Parallel Programming) — render as Coming Soon placeholders, no content build
- Sp11 Kannan PENDING — bio not yet provided by client
- Beach Villa — RETIRE recommended (not in Brochure §13 villa types)
- Treatments Details template — RETIRE recommended (redundant with 15 Tx instances)
