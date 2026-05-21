SFT_SYSTEM_PROMPT = (
    "You are an expert Audio Description (AD) writer for the visually impaired. "
    "Your task is to refine the rough video draft into a professional, vivid, and objective AD script. "
    "Strictly obey the rules: 1. NEVER use 'We see' or 'The video shows'. "
    "2. Prioritize spatial layout and vivid action descriptions. 3. Maintain emotional neutrality."
)

# from paper 
FULL_42_GUIDELINES = """
Instruction #1. Avoid over-describing — Do not include non-essential visual details.
Instruction #2. Description should not be opinionated unless content demands it.
Instruction #3. Choose level of detail based on plot relevance when describing scenes.
Instruction #4. Description should be informative and conversational, in present tense and third-person omniscient.
Instruction #5. The vocabulary should ensure accuracy, clarity, and conciseness.
Instruction #6. Consider historical context and avoid words with negative connotations or bias.
Instruction #7. Pay attention to verbs — Choose vivid verbs over bland ones with adverbs.
Instruction #8. Use pronouns only when clear whom they refer to.
Instruction #9. Use comparisons for shapes and sizes with familiar and globally relevant objects.
Instruction #10. Maintain consistency in word choice, character qualities, and visual elements.
Instruction #11. Tone and vocabulary should match the target audience’s age range.
Instruction #12. Ensure no errors in word selection, pronunciation, diction, or enunciation.
Instruction #13. Start with general context, then add details.
Instruction #14. Describe shape, size, texture, or color as appropriate to the content.
Instruction #15. Use first-person narrative for engagement if required to engage the audience.
Instruction #16. Use articles appropriately to introduce or refer to subjects.
Instruction #17. Prefer formal speech over colloquialisms, except where appropriate.
Instruction #18. When introducing new terms, label them first, and then follow with the definitions.
Instruction #19. Describe objectively without personal interpretation or comment. Also, do not censor content.
Instruction #20. Deliver narration steadily and impersonally (but not monotonously).
Instruction #21. Adjust style for emotion and mood according to the program’s genre.
Instruction #22. If it is children’s content, tailor language and pace for children’s TV.
Instruction #23. Do not alter, filter, or exclude content. Seek simplicity and succinctness.
Instruction #24. Prioritize what is relevant when describing action as to not affect user experience.
Instruction #25. Include location, time, and weather conditions when relevant to the scene or plot.
Instruction #26. Focus on key content for learning and enjoyment.
Instruction #27. When describing an instructional video, describe the sequence of activities first.
Instruction #28. For a dramatic production, include style, setting, dress, facial features, and aesthetics.
Instruction #29. Describe what is most essential for the viewer to follow and understand learning outcomes.
Instruction #30. The description should describe characters, locations, on-screen action, and on-screen information.
Instruction #31. Describe only what a sighted viewer can see.
Instruction #32. Describe characters' visual aspects relevant to identity. Use person-first language.
Instruction #33. If unable to confirm, do not guess or assume racial, ethnic or gender identity.
Instruction #34. When naming characters for the first time, include a descriptor before the name (e.g., 'a bearded man, Jack').
Instruction #35. Description should convey facial expressions, body language and reactions.
Instruction #36. When important to the intent, describe race using currently-accepted terminology.
Instruction #37. Avoid identifying characters solely by gender expression unless it offers unique insights.
Instruction #38. Describe character clothing if it enhances characterization or plot.
Instruction #39. If text on the screen is central, read the on-screen words after announcing 'Words appear'.
Instruction #40. In the case of subtitles, read the translation after stating that a subtitle appears.
Instruction #41. When shot changes are critical, indicate them by describing the new location/characters.
Instruction #42. Provide description before the content rather than after.
"""

IMPAIRMENT_INSTRUCTIONS = {
    "Blind (全盲)": " USER IS BLIND: They have zero visual input. Focus intensely on spatial geometry, object textures, precise background/foreground positioning, and auditory source anchoring. Make it a cinema for the ears.",
    "Low Vision (弱视)": " USER HAS LOW VISION: They have residual sight but blur/contrast issues. Focus intensely on color enhancement, text reading (Instruction #39), and making subtle actions or rapid shot-changes (Instruction #41) high-contrast and clear."
}

def get_inference_prompt(draft, rga_samples, lang="English", impairment="Blind (全盲)"):
  
    impair_hint = IMPAIRMENT_INSTRUCTIONS.get(impairment, "")
    

    sample_str = ""
    for i, s in enumerate(rga_samples):
        sample_str += f"Example {i+1}:\n[Rough Draft]: {s['draft']}\n[Expert AD]: {s['golden']}\n\n"
        
    prompt = f"""You are a master Audio Description (AD) specialist. Review the 42 official guidelines and the expert examples below to rewrite the current input draft into a flawless AD script.

[OFFICIAL 42 GUIDELINES]
{FULL_42_GUIDELINES}

[PERSONALIZATION CRITERIA]
{impair_hint}

[LEARNT EXPERT EXAMPLES FROM KNOWLEDGE BASE]
{sample_str}

[YOUR CURRENT TASK]
Input Rough Draft: {draft}

Please directly output the refined expert AD script. Do not include any conversational filler or explanation."""

    if lang == "Chinese":
        prompt += "\nOUTPUT REQUIREMENT: Please output the final script in Chinese (中文)."
        
    return prompt