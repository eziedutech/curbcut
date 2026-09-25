export const PRINCIPLES = ["perceivable", "operable", "understandable", "robust"] as const;

export const PRINCIPLE_LABEL: Record<(typeof PRINCIPLES)[number], string> = {
  perceivable: "Perceivable",
  operable: "Operable",
  understandable: "Understandable",
  robust: "Robust",
};

export const shortSha = (sha: string) => sha.slice(0, 7);
