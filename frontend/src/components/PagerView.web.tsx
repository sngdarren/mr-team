import React, { useRef, useEffect } from 'react';
import { ScrollView, View, Dimensions } from 'react-native';

const { height } = Dimensions.get('window');

interface PagerViewProps {
  style?: any;
  initialPage?: number;
  orientation?: 'horizontal' | 'vertical';
  onPageSelected?: (e: { nativeEvent: { position: number } }) => void;
  children: React.ReactNode;
}

/**
 * Web-compatible PagerView replacement
 * Uses ScrollView with snap scrolling to mimic PagerView behavior
 */
export default function PagerView({
  style,
  initialPage = 0,
  orientation = 'horizontal',
  onPageSelected,
  children,
}: PagerViewProps) {
  const scrollViewRef = useRef<ScrollView>(null);
  const currentPage = useRef(0);
  const isScrolling = useRef(false);

  useEffect(() => {
    // Scroll to initial page on mount
    if (scrollViewRef.current && initialPage > 0) {
      scrollViewRef.current.scrollTo({
        y: orientation === 'vertical' ? initialPage * height : 0,
        x: orientation === 'horizontal' ? initialPage * height : 0,
        animated: false,
      });
    }
  }, []);

  const handleScroll = (event: any) => {
    if (isScrolling.current) return;

    const offsetY = event.nativeEvent.contentOffset.y;
    const page = Math.round(offsetY / height);

    if (page !== currentPage.current) {
      currentPage.current = page;
      onPageSelected?.({ nativeEvent: { position: page } });
    }
  };

  const handleScrollBeginDrag = () => {
    isScrolling.current = true;
  };

  const handleScrollEndDrag = () => {
    isScrolling.current = false;
  };

  return (
    <ScrollView
      ref={scrollViewRef}
      style={style}
      pagingEnabled
      showsVerticalScrollIndicator={false}
      showsHorizontalScrollIndicator={false}
      onScroll={handleScroll}
      onScrollBeginDrag={handleScrollBeginDrag}
      onScrollEndDrag={handleScrollEndDrag}
      scrollEventThrottle={16}
      decelerationRate="fast"
      snapToInterval={height}
      snapToAlignment="start"
    >
      {children}
    </ScrollView>
  );
}

// Export the event type for compatibility
export type PagerViewOnPageSelectedEvent = {
  nativeEvent: { position: number };
};
