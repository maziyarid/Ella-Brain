import { reduce, type ChannelState } from "./machine.ts";

export const MIC_OPEN_NOTE =
  "Microphone is open for this turn. Audio is not uploaded or recorded.";
export const MIC_DENIED_NOTE =
  "Microphone permission denied. Type the utterance. No audio was stored.";
export const SPEECH_FAIL_NOTE =
  "Spoken audio failed. The text reply stands. You can still accept, reject, or type. Nothing extra was stored.";

/** Device-speech outcome only. Does not change channel phase or memory. */
export function noteAfterMicrophone(granted: boolean): string {
  return granted ? MIC_OPEN_NOTE : MIC_DENIED_NOTE;
}

/** Speech-synthesis failure leaves the text reply and returns toward listening. */
export function afterSpokenAudioFailure(state: ChannelState, epoch: number): ChannelState {
  const listening = reduce(state, {
    type: "speak_done",
    epoch,
    sessionId: state.sessionId ?? "",
  });
  return { ...listening, note: SPEECH_FAIL_NOTE };
}
