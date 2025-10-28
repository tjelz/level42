import type { ComponentProps, CSSProperties, ReactNode } from "react";

// Simple cn utility function
const cn = (...classes: (string | undefined | null | false)[]) => {
  return classes.filter(Boolean).join(' ');
};

export const XPText = ({
  children,
  className,
  style,
  ...props
}: {
  children: ReactNode;
  className?: string;
  style?: CSSProperties;
} & ComponentProps<"span">) => {
  return (
    <span
      className={cn("select-none font-bold xp-font-large", className)}
      style={{
        ...style,
        textShadow: "1px 1px 2px rgba(0, 0, 0, 0.3)",
        color: "#000080",
      }}
      {...props}
    >
      {children}
    </span>
  );
};

export default XPText;