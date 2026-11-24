# Tagging decisions (Eli, 2026-11-14)

The final scheme is column `tag_final` in `proposed_tags.csv`, produced by `code/tag_rules.py`. The draft `tag_main` and `tag_alt` columns are kept as sensitivities.

| Call | Decision |
|---|---|
| AI scope | Narrow list only: lines 49, 50, 51, 71. Line 258 (financial fees) and TVs/audio/video stay in the alt sensitivity. |
| AI vs tariff | AI ahead of tariff for PCs and phones. **To verify:** the 2025 reciprocal-tariff exemption for computers and smartphones, from a primary source. |
| Rx and non-Rx drugs (123, 124) | Untagged in final, because realized pharma tariffs were about 0 (Minneapolis Fed, Apr 8 2026). Kept in the sensitivity runs. |
| Tariff cutoff | Goods with a direct import share of purchasers' value ≥ 15%. |
| Energy cutoff | Top quartile by core weight (E ≥ 3.47%): "the most energy-intensive quarter of core spending." The strict 5% cutoff is the robustness check. Results are sensitive to the cutoff because many items bunch between 4% and 5%, so show both. |
| Odd tags | Lotteries (228) overridden to untagged, because its energy share is an I-O mapping artifact. Water/sewage and membership clubs kept as energy. |
| Transport | Fuel only. Counting all transport as energy is a sensitivity. |
| Used vehicles | Untagged. |

**Final counts (core weight):**
- AI: 4 items, 2.0%
- Tariff: 30 items, 11.1%
- Energy: 42 items, 18.3%
- Untagged: 73 items, 68.6%

**Status:**
- Not independently verified against the I-O tables.
- Not Codex-audited.
- Duplicate files from a double agent run are in `_superseded/`.
