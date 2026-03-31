/**
 * Mars IT School — Mars ID SSO integration
 */

// plane imports
import { useSearchParams } from "next/navigation";
import { API_BASE_URL } from "@plane/constants";
import type { TOAuthConfigs, TOAuthOption } from "@plane/types";

const MarsIdIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 2L2 7v10l10 5 10-5V7L12 2z" fill="#7C3AED" />
    <path d="M12 6l-5 2.5v5L12 16l5-2.5v-5L12 6z" fill="white" />
  </svg>
);

export const useExtendedOAuthConfig = (oauthActionText: string): TOAuthConfigs => {
  const searchParams = useSearchParams();
  const next_path = searchParams.get("next_path");

  const oAuthOptions: TOAuthOption[] = [
    {
      id: "mars_id",
      text: `${oauthActionText} with Mars ID`,
      icon: <MarsIdIcon />,
      onClick: () => {
        window.location.assign(`${API_BASE_URL}/auth/mars-id/${next_path ? `?next_path=${next_path}` : ``}`);
      },
      enabled: true,
    },
  ];

  return {
    isOAuthEnabled: true,
    oAuthOptions,
  };
};
