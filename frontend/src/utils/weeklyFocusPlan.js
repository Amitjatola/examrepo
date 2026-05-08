/**
 * Rule-based weekly focus suggestions (Dashboard). Not a calendar or optimizer.
 */

const ACCURACY_FLOOR_BY_BAND = {
    qualifying: 55,
    good: 65,
    ranker: 78,
}

/**
 * @param {object} params
 * @param {Record<string, number>} [params.topicPerformance]
 * @param {Record<string, number>} [params.topicAvgTimeSeconds]
 * @param {number} [params.timeTargetSeconds]
 * @param {number} [params.remediationCount]
 * @param {{ due_today?: number, current_streak?: number } | null} [params.revStats]
 * @param {string} [params.plannerTarget]
 * @param {string} [params.plannerDays]
 * @param {string} [params.plannerMode]
 * @param {number} [params.attemptsLast7Days]
 * @param {boolean} [params.includeMock]
 * @param {number} [params.maxBlocks]
 * @returns {{ id: string, title: string, reason: string, action: string, topic?: string }[]}
 */
export const buildWeeklyFocusPlan = ({
    topicPerformance = {},
    topicAvgTimeSeconds = {},
    timeTargetSeconds = 150,
    remediationCount = 0,
    revStats = null,
    plannerTarget = 'good',
    plannerDays = '30',
    plannerMode = 'smart',
    attemptsLast7Days = 0,
    includeMock = true,
    maxBlocks = 5,
} = {}) => {
    const blocks = []
    const usedTopics = new Set()
    const hasAction = (action) => blocks.some((b) => b.action === action)

    const push = (block) => {
        if (blocks.length >= maxBlocks) return
        if (block.action === 'weakTopic' || block.action === 'pacing') {
            if (!block.topic || usedTopics.has(block.topic)) return
            usedTopics.add(block.topic)
        }
        if (block.action === 'mock' && !includeMock) return
        if (block.action === 'mock' && hasAction('mock')) return
        blocks.push(block)
    }

    const due = Number(revStats?.due_today ?? 0)
    if (due > 0) {
        const streak = Number(revStats?.current_streak ?? 0)
        push({
            id: 'revision',
            title: 'Clear revision queue',
            reason: `${due} card${due === 1 ? '' : 's'} due today${streak ? ` · streak ${streak}d` : ''}.`,
            action: 'revision',
        })
    }

    const entries = Object.entries(topicPerformance).filter(([, acc]) => typeof acc === 'number')
    entries.sort((a, b) => a[1] - b[1])

    const bandKey = plannerTarget in ACCURACY_FLOOR_BY_BAND ? plannerTarget : 'good'
    const floor = ACCURACY_FLOOR_BY_BAND[bandKey]

    let weakTopicPick = null
    if (entries.length > 0) {
        const below = entries.find(([, acc]) => acc < floor)
        if (below) {
            weakTopicPick = below[0]
            push({
                id: 'weak-topic',
                title: `Drill weak topic: ${below[0]}`,
                reason: `${below[0]} is at ${below[1]}% accuracy, below your ${bandKey} band floor (${floor}%).`,
                action: 'weakTopic',
                topic: below[0],
            })
        } else {
            const worst = entries[0]
            weakTopicPick = worst[0]
            push({
                id: 'weak-topic',
                title: `Drill weak topic: ${worst[0]}`,
                reason: `${worst[0]} has your lowest heatmap accuracy (${worst[1]}%).`,
                action: 'weakTopic',
                topic: worst[0],
            })
        }
    }

    if (remediationCount > 0) {
        push({
            id: 'remediation',
            title: 'Fix recent mistakes',
            reason: `${remediationCount} recent incorrect ${remediationCount === 1 ? 'attempt' : 'attempts'} to review.`,
            action: 'remediation',
        })
    }

    const slowEntries = Object.entries(topicAvgTimeSeconds || {})
        .filter(([, sec]) => typeof sec === 'number' && sec > timeTargetSeconds)
        .sort((a, b) => b[1] - a[1])

    if (slowEntries.length > 0) {
        const [topic, avg] = slowEntries[0]
        if (topic && topic !== weakTopicPick) {
            push({
                id: 'pacing',
                title: `Pacing: ${topic}`,
                reason: `Avg ${Math.round(avg)}s per attempt vs your ${timeTargetSeconds}s target — short timed sets help.`,
                action: 'pacing',
                topic,
            })
        }
    }

    const crash = plannerDays === '5'
    const yieldMode = plannerMode === 'yield'
    const shouldMockStrong = crash || yieldMode
    const shouldMockSoft = attemptsLast7Days >= 10

    if (includeMock && blocks.length < maxBlocks && (shouldMockStrong || shouldMockSoft)) {
        const title = shouldMockStrong ? 'Run a timed mock' : 'Optional: timed block this week'
        const reason = crash
            ? 'Crash window — one full pass checks stamina and gaps.'
            : yieldMode
              ? 'Yield mode: a mock balances weak topics with exam-style pressure.'
              : 'You have steady volume — a weekly mock keeps timing honest.'
        push({
            id: 'mock',
            title,
            reason,
            action: 'mock',
        })
    }

    return blocks
}

/**
 * Whether the user has enough dashboard signals to tailor the plan (vs empty/onboarding state).
 */
export const hasWeeklyFocusSignals = ({
    topicPerformance = {},
    remediationCount = 0,
    revStats = null,
} = {}) => {
    const topics = Object.keys(topicPerformance || {}).length
    const due = Number(revStats?.due_today ?? 0)
    const rem = Number(remediationCount ?? 0)
    return topics > 0 || due > 0 || rem > 0
}
