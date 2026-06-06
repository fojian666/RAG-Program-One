import { useEffect, useRef, useState } from "react";
import { useLocation } from "react-router-dom";

export default function PageTransition({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const [displayChildren, setDisplayChildren] = useState(children);
  const [transitionClass, setTransitionClass] = useState("page-enter");
  const prevPath = useRef(location.pathname);

  useEffect(() => {
    if (location.pathname !== prevPath.current) {
      // start exit
      setTransitionClass("page-exit");
      const timer = setTimeout(() => {
        setDisplayChildren(children);
        prevPath.current = location.pathname;
        setTransitionClass("page-enter");
      }, 180);
      return () => clearTimeout(timer);
    } else {
      setDisplayChildren(children);
    }
  }, [location.pathname, children]);

  return (
    <div className={`page-transition-wrapper ${transitionClass}`}>
      {displayChildren}
    </div>
  );
}
