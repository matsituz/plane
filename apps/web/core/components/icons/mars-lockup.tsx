export function MarsLockup({ height = 24 }: { height?: number }) {
  return (
    <div className="flex items-center gap-2">
      <svg
        width={height}
        height={height}
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path d="M12 2L2 7v10l10 5 10-5V7L12 2z" fill="#7C3AED" />
        <path d="M12 6l-5 2.5v5L12 16l5-2.5v-5L12 6z" fill="white" />
      </svg>
      <span
        className="text-primary font-semibold tracking-tight"
        style={{ fontSize: height * 0.8 }}
      >
        Mars PM
      </span>
    </div>
  );
}
