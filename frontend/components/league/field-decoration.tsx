const LINE = "border-[1.5px] border-border";

const SIDE_CLASSES = {
  left: {
    edge: "left-0",
    goal: "right-full",
    spot: "left-[115px]",
    arcWindow: "left-[170px]",
    arcCircle: "-left-[146px]",
  },
  right: {
    edge: "right-0",
    goal: "left-full",
    spot: "right-[115px]",
    arcWindow: "right-[170px]",
    arcCircle: "-right-[146px]",
  },
} as const;

function PitchSide({ side }: { side: keyof typeof SIDE_CLASSES }) {
  const classes = SIDE_CLASSES[side];

  return (
    <>
      <div
        className={`absolute top-1/2 h-87.5 w-42.5 -translate-y-1/2 ${LINE} ${classes.edge}`}
      />
      <div
        className={`absolute top-1/2 h-40 w-15 -translate-y-1/2 ${LINE} ${classes.edge}`}
      />
      <div
        className={`absolute top-1/2 h-20 w-4 -translate-y-1/2 rounded-sm ${LINE} ${classes.goal}`}
      />
      <div
        className={`absolute top-1/2 size-1.5 -translate-y-1/2 rounded-full bg-border ${classes.spot}`}
      />
      {/* Meia-lua: só o pedaço do círculo que fica fora da grande área. */}
      <div
        className={`absolute top-1/2 h-45.5 w-10 -translate-y-1/2 overflow-hidden ${classes.arcWindow}`}
      >
        <div
          className={`absolute top-0 size-45.5 rounded-full ${LINE} ${classes.arcCircle}`}
        />
      </div>
    </>
  );
}

export function FieldDecoration() {
  return (
    <div
      aria-hidden
      className={`pointer-events-none absolute inset-x-30 inset-y-25 hidden rounded-[24px] xl:block ${LINE}`}
    >
      <div className="absolute inset-y-0 left-1/2 w-[1.5px] -translate-x-1/2 bg-border" />
      <div
        className={`absolute top-1/2 left-1/2 size-75 -translate-x-1/2 -translate-y-1/2 rounded-full ${LINE}`}
      />
      <div className="absolute top-1/2 left-1/2 size-1.75 -translate-x-1/2 -translate-y-1/2 rounded-full bg-border" />
      <PitchSide side="left" />
      <PitchSide side="right" />
    </div>
  );
}
