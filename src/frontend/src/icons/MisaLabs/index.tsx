import React, { forwardRef } from "react";
import SvgMisaLabs from "./MisaLabsIcon";

export const MisaLabsIcon = forwardRef<
  SVGSVGElement,
  React.PropsWithChildren<{}>
>((props, ref) => {
  return <SvgMisaLabs ref={ref} {...props} />;
});
