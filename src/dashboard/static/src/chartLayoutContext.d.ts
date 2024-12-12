import React, { ReactNode } from 'react';
import { CartesianViewBox, ChartOffset, XAxisMap, YAxisMap } from '../util/types';
import type { CategoricalChartState } from '../chart/types';
import type { Props as XAxisProps } from '../cartesian/XAxis';
import type { Props as YAxisProps } from '../cartesian/YAxis';
export declare const XAxisContext: React.Context<XAxisMap>;
export declare const YAxisContext: React.Context<YAxisMap>;
export declare const ViewBoxContext: React.Context<CartesianViewBox>;
export declare const OffsetContext: React.Context<ChartOffset>;
export declare const ClipPathIdContext: React.Context<string>;
export declare const ChartHeightContext: React.Context<number>;
export declare const ChartWidthContext: React.Context<number>;
export declare const ChartLayoutContextProvider: (props: {
    state: CategoricalChartState;
    children: ReactNode;
    clipPathId: string;
    width: number;
    height: number;
}) => React.JSX.Element;
export declare const useClipPathId: () => string | undefined;
export declare const useXAxisOrThrow: (xAxisId: string | number) => XAxisProps;
export declare const useArbitraryXAxis: () => XAxisProps | undefined;
export declare const useArbitraryYAxis: () => XAxisProps | undefined;
export declare const useYAxisWithFiniteDomainOrRandom: () => YAxisProps | undefined;
export declare const useYAxisOrThrow: (yAxisId: string | number) => YAxisProps;
export declare const useViewBox: () => CartesianViewBox;
export declare const useOffset: () => ChartOffset;
export declare const useChartWidth: () => number;
export declare const useChartHeight: () => number;