import React, { useState, useEffect } from 'react';
import Footer from '@theme-original/DocItem/Footer';
import GiscusComponent from "@site/src/components/GiscusComponent";
import HagicodeAd from "@site/src/components/HagicodeAd";
import HagicodeModal from "@site/src/components/HagicodeModal";
import { shouldShowModal } from "@site/src/components/HagicodeConfig";

export default function FooterWrapper(props) {
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    // Check if modal should be shown
    const shouldShow = shouldShowModal();
    console.log('[HagicodeModal] shouldShowModal result:', shouldShow);
    if (shouldShow) {
      setShowModal(true);
    }
  }, []);

  let weixinContent = (
    <div className="fig-author-figure-title">
      <div>
        欢迎关注的我微信公众号，第一时间获取我的最新文章。
      </div>
      <img src="/images/weixin_public.png" className="author-wechat"/>
    </div>
  );
  return (
    <>
      <Footer {...props} />
      <hr />
      {weixinContent}
      <HagicodeAd />
      <GiscusComponent/>
      <HagicodeModal isOpen={showModal} onClose={() => setShowModal(false)} />
    </>
  );
}
