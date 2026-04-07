import React from 'react';
import Footer from '@theme-original/Footer';
import {Helmet} from "react-helmet";

export default function FooterWrapper(props) {
  return (
    <>
      <Footer {...props} />
      <script src="https://sdk.jinrishici.com/v2/browser/jinrishici.js" charSet="utf-8"></script>
      <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4138796439241260"
              crossOrigin="anonymous"></script>
      <Helmet>
        <script>
          {`
var _mtac = {};
(function () {
  var mta = document.createElement('script');
  mta.src = '//pingjs.qq.com/h5/stats.js?v2.0.4';
  mta.setAttribute('name', 'MTAH5');
  mta.setAttribute('sid', '500724123');

  var s = document.getElementsByTagName('script')[0];
  s.parentNode.insertBefore(mta, s);
})();


(function(c,l,a,r,i,t,y){
  c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
  t=l.createElement(r);t.async=1;t.src='https://www.clarity.ms/tag/'+i;
  y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
})(window, document, 'clarity', 'script', 'j15shshi6c');
          `}
        </script>
      </Helmet>
    </>
  );
}
