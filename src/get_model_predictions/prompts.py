PYTHIA_CLAIM_PROMPT_0_SHOT = """Is the following claim True or False? If you are not sure or cannot answer, say None.

Claimant: <claimant>
Claim: "<claim>"
Answer:"""

PYTHIA_CLAIM_PROMPT_0_SHOT_ALT_1 = """Is the following claim True or False? Answer None if you are not sure or cannot answer.

Claimant: <claimant>
Claim: "<claim>"
Answer:"""

PYTHIA_CLAIM_PROMPT_2_SHOT = """Here are some claims made by different claimants. Are the claims True or False? If you are not sure or cannot answer, say None.

Claimant: Joe Biden
Claim: "“One quarter” of today’s $31.4 trillion federal debt “was accumulated in the four years of my predecessor,” Donald Trump."
Answer: True

Claimant: Viral post
Claim: "the new coronavirus has HIV proteins that indicate it was genetically modified in a laboratory."
Answer: False

Claimant: <claimant>
Claim: "<claim>"
Answer:"""

PYTHIA_CLAIM_PROMPT_2_SHOT_ALT_1 = """Are the following claims True or False? Say None if you are not sure or cannot answer.

Claimant: Joe Biden
Claim: "“One quarter” of today’s $31.4 trillion federal debt “was accumulated in the four years of my predecessor,” Donald Trump."
Answer: True

Claimant: Viral post
Claim: "the new coronavirus has HIV proteins that indicate it was genetically modified in a laboratory."
Answer: False

Claimant: <claimant>
Claim: "<claim>"
Answer:"""

PYTHIA_CLAIM_PROMPT_2_SHOT_ALT_2 = """Are the following claims True or False? Answer None if you are not sure or cannot answer.

Claimant: Joe Biden
Claim: "“One quarter” of today’s $31.4 trillion federal debt “was accumulated in the four years of my predecessor,” Donald Trump."
Answer: True

Claimant: Viral post
Claim: "the new coronavirus has HIV proteins that indicate it was genetically modified in a laboratory."
Answer: False

Claimant: <claimant>
Claim: "<claim>"
Answer:"""

PYTHIA_CLAIM_PROMPT_2_SHOT_ALT_3 = """Are the following claims correct? Yes, No or Not sure?

Claimant: Joe Biden
Claim: "“One quarter” of today’s $31.4 trillion federal debt “was accumulated in the four years of my predecessor,” Donald Trump."
Answer: Yes

Claimant: Viral post
Claim: "the new coronavirus has HIV proteins that indicate it was genetically modified in a laboratory."
Answer: No

Claimant: <claimant>
Claim: "<claim>"
Answer:"""

PYTHIA_CLAIM_PROMPT_3_SHOT = """Are the following claims True or False? Answer None if you are not sure or cannot answer.

Claimant: Joe Biden
Claim: "“One quarter” of today’s $31.4 trillion federal debt “was accumulated in the four years of my predecessor,” Donald Trump."
Answer: True

Claimant: Viral post
Claim: "the new coronavirus has HIV proteins that indicate it was genetically modified in a laboratory."
Answer: False

Claimant: Sara Daniels
Claim: "Blackpink released the single 'You me too' in 2026."
Answer: None

Claimant: <claimant>
Claim: "<claim>"
Answer:"""

PYTHIA_CLAIM_PROMPT_3_SHOT_NO_CLAIMANT = """Are the following claims True or False? Answer None if you are not sure or cannot answer.

Claim: "“One quarter” of today’s $31.4 trillion federal debt “was accumulated in the four years of my predecessor,” Donald Trump."
Answer: True

Claim: "the new coronavirus has HIV proteins that indicate it was genetically modified in a laboratory."
Answer: False

Claim: "Blackpink released the single 'You me too' in 2026."
Answer: None

Claim: "<claim>"
Answer:"""

PYTHIA_CLAIM_PROMPT_3_SHOT_ALT_1 = """Are the following claims True or False? Answer None if you are not sure or cannot answer.

Claimant: Joe Biden
Claim: "“One quarter” of today’s $31.4 trillion federal debt “was accumulated in the four years of my predecessor,” Donald Trump."
Answer: True

Claimant: Viral post
Claim: "5G causes cancer."
Answer: False

Claimant: Sara Daniels
Claim: "Blackpink released the single 'You me too' in 2026."
Answer: None

Claimant: <claimant>
Claim: "<claim>"
Answer:"""

PYTHIA_CLAIM_PROMPT_3_SHOT_ALT_1_NO_CLAIMANT = """Are the following claims True or False? Answer None if you are not sure or cannot answer.

Claim: "“One quarter” of today’s $31.4 trillion federal debt “was accumulated in the four years of my predecessor,” Donald Trump."
Answer: True

Claim: "5G causes cancer."
Answer: False

Claim: "Blackpink released the single 'You me too' in 2026."
Answer: None

Claim: "<claim>"
Answer:"""

PYTHIA_EVIDENCE_PROMPT_0_SHOT = """Based on the provided evidence, is the claim True or False? If you are not sure or cannot answer, say None.

Claimant: <claimant>
Claim: "<claim>"
Evidence: "<evidence>"
Answer:"""

PYTHIA_EVIDENCE_PROMPT_2_SHOT = """Here are some claims and accompanying evidence pieces. Based on the evidence pieces, are the claims True or False? If you are not sure or cannot answer, say None.

Claimant: Joe Biden
Claim: "“One quarter” of today’s $31.4 trillion federal debt “was accumulated in the four years of my predecessor,” Donald Trump."
Evidence: "Biden’s number is accurate; about one-fourth of the total debt incurred to date came on Trump’s watch. However, assigning debt to a particular president is tricky, because so much of the spending was approved by decades-old, bipartisan legislation that set the parameters for Social Security and Medicare. A different calculation shows more debt stemming from former President Barack Obama, with whom Biden served as vice president."
Answer: True

Claimant: Viral post
Claim: "the new coronavirus has HIV proteins that indicate it was genetically modified in a laboratory."
Evidence: "Microbiologists say the spike proteins found in the new coronavirus are different from the ones found in HIV. [...] There is no evidence to suggest the coronavirus was genetically modified."
Answer: False

Claimant: <claimant>
Claim: "<claim>"
Evidence: "<evidence>"
Answer:"""

PYTHIA_EVIDENCE_PROMPT_2_SHOT_ALT_1 = """Based on the provided evidence, are the claims True or False? If you are not sure or cannot answer, say None.

Claimant: Joe Biden
Claim: "“One quarter” of today’s $31.4 trillion federal debt “was accumulated in the four years of my predecessor,” Donald Trump."
Evidence: "Biden’s number is accurate; about one-fourth of the total debt incurred to date came on Trump’s watch. However, assigning debt to a particular president is tricky, because so much of the spending was approved by decades-old, bipartisan legislation that set the parameters for Social Security and Medicare. A different calculation shows more debt stemming from former President Barack Obama, with whom Biden served as vice president."
Answer: True

Claimant: Viral post
Claim: "the new coronavirus has HIV proteins that indicate it was genetically modified in a laboratory."
Evidence: "Microbiologists say the spike proteins found in the new coronavirus are different from the ones found in HIV. [...] There is no evidence to suggest the coronavirus was genetically modified."
Answer: False

Claimant: <claimant>
Claim: "<claim>"
Evidence: "<evidence>"
Answer:"""

PYTHIA_EVIDENCE_PROMPT_2_SHOT_ALT_2 = """Are the claims True or False based on the accompanying evidence? If you are not sure or cannot answer, say None.

Claimant: Joe Biden
Claim: "“One quarter” of today’s $31.4 trillion federal debt “was accumulated in the four years of my predecessor,” Donald Trump."
Evidence: "Biden’s number is accurate; about one-fourth of the total debt incurred to date came on Trump’s watch. However, assigning debt to a particular president is tricky, because so much of the spending was approved by decades-old, bipartisan legislation that set the parameters for Social Security and Medicare. A different calculation shows more debt stemming from former President Barack Obama, with whom Biden served as vice president."
Answer: True

Claimant: Viral post
Claim: "the new coronavirus has HIV proteins that indicate it was genetically modified in a laboratory."
Evidence: "Microbiologists say the spike proteins found in the new coronavirus are different from the ones found in HIV. [...] There is no evidence to suggest the coronavirus was genetically modified."
Answer: False

Claimant: <claimant>
Claim: "<claim>"
Evidence: "<evidence>"
Answer:"""

PYTHIA_EVIDENCE_PROMPT_2_SHOT_ALT_3 = """Are the claims True or False according to the accompanying evidence? If the evidence supports a bit of both, say "Disputed". If there is not enough information to conclude, say "Not enough information".

Claimant: Joe Biden
Claim: "“One quarter” of today’s $31.4 trillion federal debt “was accumulated in the four years of my predecessor,” Donald Trump."
Evidence: "Biden’s number is accurate; about one-fourth of the total debt incurred to date came on Trump’s watch. However, assigning debt to a particular president is tricky, because so much of the spending was approved by decades-old, bipartisan legislation that set the parameters for Social Security and Medicare. A different calculation shows more debt stemming from former President Barack Obama, with whom Biden served as vice president."
Answer: True

Claimant: Viral post
Claim: "the new coronavirus has HIV proteins that indicate it was genetically modified in a laboratory."
Evidence: "Microbiologists say the spike proteins found in the new coronavirus are different from the ones found in HIV. [...] There is no evidence to suggest the coronavirus was genetically modified."
Answer: False

Claimant: <claimant>
Claim: "<claim>"
Evidence: "<evidence>"
Answer:"""

PYTHIA_EVIDENCE_PROMPT_3_SHOT = """Based on the provided evidence, are the claims True or False? If you are not sure or cannot answer, say None.

Claimant: Joe Biden
Claim: "“One quarter” of today’s $31.4 trillion federal debt “was accumulated in the four years of my predecessor,” Donald Trump."
Evidence: "Biden’s number is accurate; about one-fourth of the total debt incurred to date came on Trump’s watch. However, assigning debt to a particular president is tricky, because so much of the spending was approved by decades-old, bipartisan legislation that set the parameters for Social Security and Medicare. A different calculation shows more debt stemming from former President Barack Obama, with whom Biden served as vice president."
Answer: True

Claimant: Viral post
Claim: "the new coronavirus has HIV proteins that indicate it was genetically modified in a laboratory."
Evidence: "Microbiologists say the spike proteins found in the new coronavirus are different from the ones found in HIV. [...] There is no evidence to suggest the coronavirus was genetically modified."
Answer: False

Claimant: Sara Daniels
Claim: "Blackpink released the single 'You me too' in 2026."
Evidence: "Blackpink released their album 'Born Pink' in 2022."
Answer: None

Claimant: <claimant>
Claim: "<claim>"
Evidence: "<evidence>"
Answer:"""

PYTHIA_EVIDENCE_PROMPT_3_SHOT_ALT_1 = """Based on the provided evidence, are the claims True or False? If you are not sure or cannot answer, say None.

Claimant: Joe Biden
Claim: "“One quarter” of today’s $31.4 trillion federal debt “was accumulated in the four years of my predecessor,” Donald Trump."
Evidence: "Biden’s number is accurate; about one-fourth of the total debt incurred to date came on Trump’s watch."
Answer: True

Claimant: Viral post
Claim: "the new coronavirus has HIV proteins that indicate it was genetically modified in a laboratory."
Evidence: "Microbiologists say the spike proteins found in the new coronavirus are different from the ones found in HIV. [...] There is no evidence to suggest the coronavirus was genetically modified."
Answer: False

Claimant: Sara Daniels
Claim: "Blackpink released the single 'You me too' in 2026."
Evidence: "Blackpink released their album 'Born Pink' in 2022."
Answer: None

Claimant: <claimant>
Claim: "<claim>"
Evidence: "<evidence>"
Answer:"""

PYTHIA_EVIDENCE_PROMPT_3_SHOT_ALT_1_NO_CLAIMANT = """Based on the provided evidence, are the claims True or False? If you are not sure or cannot answer, say None.

Claim: "“One quarter” of today’s $31.4 trillion federal debt “was accumulated in the four years of my predecessor,” Donald Trump."
Evidence: "Biden’s number is accurate; about one-fourth of the total debt incurred to date came on Trump’s watch."
Answer: True

Claim: "the new coronavirus has HIV proteins that indicate it was genetically modified in a laboratory."
Evidence: "Microbiologists say the spike proteins found in the new coronavirus are different from the ones found in HIV. [...] There is no evidence to suggest the coronavirus was genetically modified."
Answer: False

Claim: "Blackpink released the single 'You me too' in 2026."
Evidence: "Blackpink released their album 'Born Pink' in 2022."
Answer: None

Claim: "<claim>"
Evidence: "<evidence>"
Answer:"""
          
PYTHIA_EVIDENCE_PROMPT_3_SHOT_ALT_2 = """Based on the provided evidence, are the claims True or False? If you are uncertain or if there is not enough info in the evidence, say None.

Claimant: Joe Biden
Claim: "“One quarter” of today’s $31.4 trillion federal debt “was accumulated in the four years of my predecessor,” Donald Trump."
Evidence: "Biden’s number is accurate; about one-fourth of the total debt incurred to date came on Trump’s watch."
Answer: True

Claimant: Viral post
Claim: "the new coronavirus has HIV proteins that indicate it was genetically modified in a laboratory."
Evidence: "Microbiologists say the spike proteins found in the new coronavirus are different from the ones found in HIV. [...] There is no evidence to suggest the coronavirus was genetically modified."
Answer: False

Claimant: Sara Daniels
Claim: "Blackpink released the single 'You me too' in 2026."
Evidence: "Blackpink released their album 'Born Pink' in 2022."
Answer: None

Claimant: <claimant>
Claim: "<claim>"
Evidence: "<evidence>"
Answer:"""
             
PYTHIA_EVIDENCE_PROMPT_3_SHOT_ALT_3 = """Based on the provided evidence, are the claims True or False? Answer None if you are not sure or cannot answer.

Claimant: Joe Biden
Claim: "“One quarter” of today’s $31.4 trillion federal debt “was accumulated in the four years of my predecessor,” Donald Trump."
Evidence: "Biden’s number is accurate; about one-fourth of the total debt incurred to date came on Trump’s watch. However, assigning debt to a particular president is tricky, because so much of the spending was approved by decades-old, bipartisan legislation that set the parameters for Social Security and Medicare. A different calculation shows more debt stemming from former President Barack Obama, with whom Biden served as vice president."
Answer: True

Claimant: Viral post
Claim: "the new coronavirus has HIV proteins that indicate it was genetically modified in a laboratory."
Evidence: "Microbiologists say the spike proteins found in the new coronavirus are different from the ones found in HIV. [...] There is no evidence to suggest the coronavirus was genetically modified."
Answer: False

Claimant: Sara Daniels
Claim: "Blackpink released the single 'You me too' in 2026."
Evidence: "Blackpink released their album 'Born Pink' in 2022."
Answer: None

Claimant: <claimant>
Claim: "<claim>"
Evidence: "<evidence>"
Answer:"""
          
PYTHIA_EVIDENCE_PROMPT_3_SHOT_ALT_4 = """Here are some claims and corresponding evidence. Does the evidence Support or Refute the claim? Answer None if there is not enough information in the evidence to decide.

Claimant: Joe Biden
Claim: "“One quarter” of today’s $31.4 trillion federal debt “was accumulated in the four years of my predecessor,” Donald Trump."
Evidence: "Biden’s number is accurate; about one-fourth of the total debt incurred to date came on Trump’s watch. However, assigning debt to a particular president is tricky, because so much of the spending was approved by decades-old, bipartisan legislation that set the parameters for Social Security and Medicare. A different calculation shows more debt stemming from former President Barack Obama, with whom Biden served as vice president."
Answer: Support

Claimant: Viral post
Claim: "the new coronavirus has HIV proteins that indicate it was genetically modified in a laboratory."
Evidence: "Microbiologists say the spike proteins found in the new coronavirus are different from the ones found in HIV. [...] There is no evidence to suggest the coronavirus was genetically modified."
Answer: Refute

Claimant: Sara Daniels
Claim: "Blackpink released the single 'You me too' in 2026."
Evidence: "Blackpink released their album 'Born Pink' in 2022."
Answer: None

Claimant: <claimant>
Claim: "<claim>"
Evidence: "<evidence>"
Answer:"""

PYTHIA_EVIDENCE_PROMPT_3_SHOT_ALT_4_NO_CLAIMANT = """Here are some claims and corresponding evidence. Does the evidence Support or Refute the claim? Answer None if there is not enough information in the evidence to decide.

Claim: "“One quarter” of today’s $31.4 trillion federal debt “was accumulated in the four years of my predecessor,” Donald Trump."
Evidence: "Biden’s number is accurate; about one-fourth of the total debt incurred to date came on Trump’s watch. However, assigning debt to a particular president is tricky, because so much of the spending was approved by decades-old, bipartisan legislation that set the parameters for Social Security and Medicare. A different calculation shows more debt stemming from former President Barack Obama, with whom Biden served as vice president."
Answer: Support

Claim: "the new coronavirus has HIV proteins that indicate it was genetically modified in a laboratory."
Evidence: "Microbiologists say the spike proteins found in the new coronavirus are different from the ones found in HIV. [...] There is no evidence to suggest the coronavirus was genetically modified."
Answer: Refute

Claim: "Blackpink released the single 'You me too' in 2026."
Evidence: "Blackpink released their album 'Born Pink' in 2022."
Answer: None

Claim: "<claim>"
Evidence: "<evidence>"
Answer:"""

PYTHIA_EVIDENCE_PROMPT_3_SHOT_ALT_5 = """Does the evidence Support or Refute the claim? Answer None if there is not enough information in the evidence to decide.

Claimant: Joe Biden
Claim: "“One quarter” of today’s $31.4 trillion federal debt “was accumulated in the four years of my predecessor,” Donald Trump."
Evidence: "Biden’s number is accurate; about one-fourth of the total debt incurred to date came on Trump’s watch. However, assigning debt to a particular president is tricky, because so much of the spending was approved by decades-old, bipartisan legislation that set the parameters for Social Security and Medicare. A different calculation shows more debt stemming from former President Barack Obama, with whom Biden served as vice president."
Answer: Support

Claimant: Viral post
Claim: "the new coronavirus has HIV proteins that indicate it was genetically modified in a laboratory."
Evidence: "Microbiologists say the spike proteins found in the new coronavirus are different from the ones found in HIV. [...] There is no evidence to suggest the coronavirus was genetically modified."
Answer: Refute

Claimant: Sara Daniels
Claim: "Blackpink released the single 'You me too' in 2026."
Evidence: "Blackpink released their album 'Born Pink' in 2022."
Answer: None

Claimant: <claimant>
Claim: "<claim>"
Evidence: "<evidence>"
Answer:"""

PYTHIA_EVIDENCE_PROMPT_3_SHOT_ALT_6 = """Does the evidence Support or Refute the claim? Answer None if there is not enough information in the evidence to decide or if you are uncertain.

Claimant: Joe Biden
Claim: "“One quarter” of today’s $31.4 trillion federal debt “was accumulated in the four years of my predecessor,” Donald Trump."
Evidence: "Biden’s number is accurate; about one-fourth of the total debt incurred to date came on Trump’s watch. However, assigning debt to a particular president is tricky, because so much of the spending was approved by decades-old, bipartisan legislation that set the parameters for Social Security and Medicare. A different calculation shows more debt stemming from former President Barack Obama, with whom Biden served as vice president."
Answer: Support

Claimant: Viral post
Claim: "the new coronavirus has HIV proteins that indicate it was genetically modified in a laboratory."
Evidence: "Microbiologists say the spike proteins found in the new coronavirus are different from the ones found in HIV. [...] There is no evidence to suggest the coronavirus was genetically modified."
Answer: Refute

Claimant: Sara Daniels
Claim: "Blackpink released the single 'You me too' in 2026."
Evidence: "Blackpink released their album 'Born Pink' in 2022."
Answer: None

Claimant: <claimant>
Claim: "<claim>"
Evidence: "<evidence>"
Answer:"""
               
PYTHIA_EVIDENCE_PROMPT_3_SHOT_ALT_7 = """Are the claims True or False based on the accompanying evidence? If you are not sure or cannot answer, say None.

Claimant: Joe Biden
Claim: "“One quarter” of today’s $31.4 trillion federal debt “was accumulated in the four years of my predecessor,” Donald Trump."
Evidence: "Biden’s number is accurate; about one-fourth of the total debt incurred to date came on Trump’s watch. However, assigning debt to a particular president is tricky, because so much of the spending was approved by decades-old, bipartisan legislation that set the parameters for Social Security and Medicare. A different calculation shows more debt stemming from former President Barack Obama, with whom Biden served as vice president."
Answer: True

Claimant: Viral post
Claim: "the new coronavirus has HIV proteins that indicate it was genetically modified in a laboratory."
Evidence: "Microbiologists say the spike proteins found in the new coronavirus are different from the ones found in HIV. [...] There is no evidence to suggest the coronavirus was genetically modified."
Answer: False

Claimant: Sara Daniels
Claim: "Blackpink released the single 'You me too' in 2026."
Evidence: "Blackpink released their album 'Born Pink' in 2022."
Answer: None

Claimant: <claimant>
Claim: "<claim>"
Evidence: "<evidence>"
Answer:"""

PYTHIA_EVIDENCE_PROMPT_3_SHOT_ALT_7_NO_CLAIMANT = """Are the claims True or False based on the accompanying evidence? If you are not sure or cannot answer, say None.

Claim: "“One quarter” of today’s $31.4 trillion federal debt “was accumulated in the four years of my predecessor,” Donald Trump."
Evidence: "Biden’s number is accurate; about one-fourth of the total debt incurred to date came on Trump’s watch. However, assigning debt to a particular president is tricky, because so much of the spending was approved by decades-old, bipartisan legislation that set the parameters for Social Security and Medicare. A different calculation shows more debt stemming from former President Barack Obama, with whom Biden served as vice president."
Answer: True

Claim: "the new coronavirus has HIV proteins that indicate it was genetically modified in a laboratory."
Evidence: "Microbiologists say the spike proteins found in the new coronavirus are different from the ones found in HIV. [...] There is no evidence to suggest the coronavirus was genetically modified."
Answer: False

Claim: "Blackpink released the single 'You me too' in 2026."
Evidence: "Blackpink released their album 'Born Pink' in 2022."
Answer: None

Claim: "<claim>"
Evidence: "<evidence>"
Answer:"""
               
PROMPT_DICT = {"pythia_claim_prompt_0_shot": PYTHIA_CLAIM_PROMPT_0_SHOT,
               "pythia_claim_prompt_0_shot_alt_1": PYTHIA_CLAIM_PROMPT_0_SHOT_ALT_1,
               "pythia_claim_prompt_2_shot": PYTHIA_CLAIM_PROMPT_2_SHOT,
               "pythia_claim_prompt_2_shot_alt_1": PYTHIA_CLAIM_PROMPT_2_SHOT_ALT_1,
               "pythia_claim_prompt_2_shot_alt_2": PYTHIA_CLAIM_PROMPT_2_SHOT_ALT_2,
               "pythia_claim_prompt_2_shot_alt_3": PYTHIA_CLAIM_PROMPT_2_SHOT_ALT_3,
               "pythia_claim_prompt_3_shot": PYTHIA_CLAIM_PROMPT_3_SHOT,
               "pythia_claim_prompt_3_shot_no_claimant": PYTHIA_CLAIM_PROMPT_3_SHOT_NO_CLAIMANT,
               "pythia_claim_prompt_3_shot_alt_1": PYTHIA_CLAIM_PROMPT_3_SHOT_ALT_1,
               "pythia_claim_prompt_3_shot_alt_1_no_claimant": PYTHIA_CLAIM_PROMPT_3_SHOT_ALT_1_NO_CLAIMANT,
               "pythia_evidence_prompt_0_shot": PYTHIA_EVIDENCE_PROMPT_0_SHOT,
               "pythia_evidence_prompt_2_shot": PYTHIA_EVIDENCE_PROMPT_2_SHOT,
               "pythia_evidence_prompt_2_shot_alt_1": PYTHIA_EVIDENCE_PROMPT_2_SHOT_ALT_1,
               "pythia_evidence_prompt_2_shot_alt_2": PYTHIA_EVIDENCE_PROMPT_2_SHOT_ALT_2,
               "pythia_evidence_prompt_2_shot_alt_3": PYTHIA_EVIDENCE_PROMPT_2_SHOT_ALT_3,
               "pythia_evidence_prompt_3_shot": PYTHIA_EVIDENCE_PROMPT_3_SHOT,
               "pythia_evidence_prompt_3_shot_alt_1": PYTHIA_EVIDENCE_PROMPT_3_SHOT_ALT_1,
               "pythia_evidence_prompt_3_shot_alt_2": PYTHIA_EVIDENCE_PROMPT_3_SHOT_ALT_2,
               "pythia_evidence_prompt_3_shot_alt_3": PYTHIA_EVIDENCE_PROMPT_3_SHOT_ALT_3,
               "pythia_evidence_prompt_3_shot_alt_4": PYTHIA_EVIDENCE_PROMPT_3_SHOT_ALT_4,
               "pythia_evidence_prompt_3_shot_alt_4_no_claimant": PYTHIA_EVIDENCE_PROMPT_3_SHOT_ALT_4_NO_CLAIMANT,
               "pythia_evidence_prompt_3_shot_alt_5": PYTHIA_EVIDENCE_PROMPT_3_SHOT_ALT_5,
               "pythia_evidence_prompt_3_shot_alt_6": PYTHIA_EVIDENCE_PROMPT_3_SHOT_ALT_6,
               "pythia_evidence_prompt_3_shot_alt_7": PYTHIA_EVIDENCE_PROMPT_3_SHOT_ALT_7,
               "pythia_evidence_prompt_3_shot_alt_7_no_claimant": PYTHIA_EVIDENCE_PROMPT_3_SHOT_ALT_7_NO_CLAIMANT}