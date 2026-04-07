import React from 'react';
import Giscus from "@giscus/react";
import { useColorMode } from '@docusaurus/theme-common';

export default function GiscusComponent() {
  const { colorMode } = useColorMode();

  return (
      <Giscus
          repo="newbe36524/Newbe.Docs"
          repoId="MDEwOlJlcG9zaXRvcnkyMzMyNTM2NjY="
          category="Announcements"
          categoryId="DIC_kwDODecrIs4CUkhR"
          mapping="pathname"                        // Important! To map comments to URL
          term="Welcome to @giscus/react component!"
          strict="0"
          reactionsEnabled="1"
          emitMetadata="1"
          inputPosition="top"
          theme={colorMode}
          lang="en"
          loading="lazy"
      />
  );
}