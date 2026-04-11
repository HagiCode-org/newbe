import React from 'react';
import Footer from '@theme-original/DocItem/Footer';
import HagicodeAd from "@site/src/components/HagicodeAd";

export default function FooterWrapper(props) {
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
    </>
  );
}
