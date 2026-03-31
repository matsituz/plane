/**
 * Mars IT School — Edition badge
 */

import { observer } from "mobx-react";
import { Tooltip } from "@plane/propel/tooltip";
import { usePlatformOS } from "@/hooks/use-platform-os";
import packageJson from "package.json";

export const WorkspaceEditionBadge = observer(function WorkspaceEditionBadge() {
  const { isMobile } = usePlatformOS();

  return (
    <Tooltip tooltipContent={`Version: v${packageJson.version}`} isMobile={isMobile}>
      <div className="flex items-center gap-1.5 rounded-md px-2 py-1 text-xs font-medium text-tertiary">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
          <path d="M12 2L2 7v10l10 5 10-5V7L12 2z" fill="#7C3AED" />
          <path d="M12 6l-5 2.5v5L12 16l5-2.5v-5L12 6z" fill="white" />
        </svg>
        Mars PM
      </div>
    </Tooltip>
  );
});
