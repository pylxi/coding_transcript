# Episode Definitions & Rules

## What is an Episode?

**Episode (Collaboration)**: A contiguous sequence of utterances that form a coherent collaborative activity (e.g., troubleshooting audio, sharing information, negotiating a decision).

### Episode Duration & Size
- **Target duration**: 1–5 minutes
- **Target utterance count**: 5–30 utterances
- Keep episodes focused on a single collaborative activity/topic

### Monologue Handling

**Monologue Definition**: If a speaker produces > 1 minute of continuous talk without the other participant(s) speaking

**Monologue Rules**:
1. **Duration threshold**: > 90 seconds (1 minute) of uninterrupted speech by one speaker
2. **NOT standalone episodes**: Monologues are part of the episode that precedes or follows them
3. **Incorporation**: Incorporate monologue into surrounding episode UNLESS:
   - Content clearly forms a separate topic
   - Followed by a partner response that shifts the collaborative function
4. **Summarization**: Summarise the monologue (e.g., "Rwitajit explains the pilot structure for 2 minutes")
5. **Example**: A consensus episode may contain:
   - A long proposal (monologue)
   - Followed by partner reactions
   - All treated as ONE episode

### Episode Boundaries

Episodes should end when:
- Topic/collaborative activity shifts significantly
- Discussion reaches natural conclusion (decision made, consensus reached)
- Monologue interrupts flow (incorporate into surrounding episode)
- Duration exceeds 5 minutes
- Utterance count exceeds 30

### Implementation Notes

- Use **similarity scoring** between consecutive utterances to detect topic shifts
- Track **speaker turns** to detect monologues
- Calculate **episode duration** from timestamp differences
- Count **utterances** per episode
