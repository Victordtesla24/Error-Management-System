import React, { ReactElement } from 'react';
import { ChartCoordinate, ChartOffset, LayoutType, TooltipEventType } from '../util/types';
export type CursorProps = {
    activeCoordinate: ChartCoordinate;
    activePayload: any[];
    activeTooltipIndex: number;
    chartName: string;
    element: ReactElement;
    isActive: boolean;
    layout: LayoutType;
    offset: ChartOffset;
    tooltipAxisBandSize: number;
    tooltipEventType: TooltipEventType;
};
export declare function Cursor(props: CursorProps): React.FunctionComponentElement<any> | React.DetailedReactHTMLElement<{
    payload: any[];
    payloadIndex: number;
    className: string;
    stroke: string;
    fill: string;
    x: number;
    y: number;
    width: number;
    height: number;
    top?: number;
    bottom?: number;
    left?: number;
    right?: number;
    brushBottom?: number;
    pointerEvents: string;
} | {
    payload: any[];
    payloadIndex: number;
    className: string;
    xAxis?: any;
    yAxis?: any;
    width?: any;
    height?: any;
    offset?: ChartOffset;
    angle?: number;
    radius?: number;
    cx?: number;
    cy?: number;
    startAngle?: number;
    endAngle?: number;
    innerRadius?: number;
    outerRadius?: number;
    x: number;
    y: number;
    top?: number;
    bottom?: number;
    left?: number;
    right?: number;
    brushBottom?: number;
    stroke: string;
    pointerEvents: string;
} | {
    payload: any[];
    payloadIndex: number;
    className: string;
    cx: number;
    cy: number;
    startAngle: number;
    endAngle: number;
    innerRadius: number;
    outerRadius: number;
    top?: number;
    bottom?: number;
    left?: number;
    right?: number;
    width?: number;
    height?: number;
    brushBottom?: number;
    stroke: string;
    pointerEvents: string;
} | {
    payload: any[];
    payloadIndex: number;
    className: string;
    points: import("../util/cursor/getRadialCursorPoints").RadialCursorPoints | [import("../util/types").Coordinate, import("../util/types").Coordinate];
    top?: number;
    bottom?: number;
    left?: number;
    right?: number;
    width?: number;
    height?: number;
    brushBottom?: number;
    stroke: string;
    pointerEvents: string;
}, HTMLElement>;