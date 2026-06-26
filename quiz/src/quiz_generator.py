"""Generate Indian-classical-themed quiz and poll content."""
import datetime


def get_post_type():
    return "poll" if datetime.date.today().weekday() == 1 else "quiz"


def generate_poll(client):
    """Tuesday: raga preference poll. Returns (question, options[4])."""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="""You are creating a Tuesday community poll for @DhunDetox — an Indian classical raga healing music channel.

Generate a raga/music preference poll that fans of Indian classical and healing music will love.

Rules:
- Question about personal music preference, feeling, or raga experience
- 4 options: each 2-4 words + 1 relevant emoji
- All options equally valid — every fan can see themselves in one
- Warm and inviting tone

Good examples:
"Which raga helps you sleep best?"
"When do you need healing music most?"
"Which feeling brings you to Indian classical music?"
"Which instrument reaches your soul?"

Output EXACTLY:
QUESTION: <question ending with ?>
OPTION_1: <emoji> <2-4 words>
OPTION_2: <emoji> <2-4 words>
OPTION_3: <emoji> <2-4 words>
OPTION_4: <emoji> <2-4 words>"""
    )

    question, options = "", []
    for line in response.text.strip().splitlines():
        line = line.strip()
        if line.startswith("QUESTION:"):
            question = line[9:].strip()
        elif line.startswith("OPTION_") and ":" in line:
            options.append(line[line.index(":") + 1:].strip())

    if not question:
        question = "Which raga helps you find peace?"
    if len(options) < 4:
        options = ["🌿 Raag Bhairavi", "🌸 Raag Bhupali", "🌙 Raag Darbari", "🎵 Raag Yaman"]

    return question, options[:4]


def generate_quiz(client):
    """Saturday: raga knowledge quiz with reveal. Returns (question, options[4], reveal)."""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="""You are creating a Saturday quiz for @DhunDetox — Indian classical raga healing music channel.

Create a raga knowledge quiz: an interesting fact or healing property of a specific raga, with 3 plausible wrong answers and 1 surprising true answer.

Rules:
- Question should be a "what is / which raga / why does" style about Indian classical music
- 3 options: plausible but wrong
- 1 option: the surprising true answer (specific, fascinating fact)
- Reveal: 2 sentences expanding on the true answer with cultural/healing context

Output EXACTLY:
QUESTION: <question ending with ?>
OPTION_A: <emoji> <5-8 words>
OPTION_B: <emoji> <5-8 words>
OPTION_C: <emoji> <5-8 words>
OPTION_D: <emoji> <5-8 words — THE TRUE ANSWER>
REVEAL: <2 sentences about why Option D is correct, cultural/healing depth>"""
    )

    question, options, reveal = "", [], ""
    reveal_lines = []
    current = None

    for line in response.text.strip().splitlines():
        line = line.strip()
        if not line and current != "reveal":
            continue
        if line.startswith("QUESTION:"):
            question, current = line[9:].strip(), None
        elif line.startswith(("OPTION_A:", "OPTION_B:", "OPTION_C:", "OPTION_D:")):
            options.append(line[line.index(":") + 1:].strip())
            current = None
        elif line.startswith("REVEAL:"):
            current = "reveal"
            first = line[7:].strip()
            if first:
                reveal_lines.append(first)
        elif current == "reveal" and line:
            reveal_lines.append(line)

    reveal = " ".join(reveal_lines)

    if not question:
        question = "Which raga is traditionally performed only at midnight?"
    if len(options) < 4:
        options = ["🌅 Raag Bhairav", "🌸 Raag Bhupali", "🌙 Raag Yaman", "✨ Raag Darbari Kanada"]
    if not reveal:
        reveal = "Raag Darbari Kanada — with its heavy, slow gamaks and deep komal notes — was composed by Miyan Tansen for Emperor Akbar's late-night court. Its gravity and weight make it impossible to sing or hear without feeling the weight of the night itself."

    return question, options[:4], reveal


def build_captions(post_type, question, options, reveal=""):
    opts_joined = " · ".join(options)
    if post_type == "poll":
        ig = f"🎵 {question}\n\n{opts_joined}\n\nDrop your answer below 👇 Let's see what the community says!"
        fb = f"🎵 {question}\n\n{opts_joined}\n\nShare your answer in the comments 👇"
    else:
        letters = ["A", "B", "C", "D"]
        opts_text = "\n".join(f"{l}. {o}" for l, o in zip(letters, options))
        ig = f"🧠 {question}\n\n{opts_text}\n\nWhat's your answer? Drop it below 👇\n\n(Reveal in comments 👇)"
        fb = f"🧠 {question}\n\n{opts_text}\n\n💡 REVEAL: {reveal}\n\nHow many got it right? 🙌"
    return ig, fb
