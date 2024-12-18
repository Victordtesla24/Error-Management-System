import React, { PureComponent, CSSProperties, ReactNode, ReactElement, SVGProps } from 'react';
import { ValueType, NameType, Payload, Props as ToltipContentProps } from './DefaultTooltipContent';
import { UniqueOption } from '../util/payload/getUniqPayload';
import { AllowInDimension, AnimationDuration, AnimationTiming, CartesianViewBox, Coordinate } from '../util/types';
export type ContentType<TValue extends ValueType, TName extends NameType> = ReactElement | ((props: TooltipProps<TValue, TName>) => ReactNode);
export type TooltipProps<TValue extends ValueType, TName extends NameType> = ToltipContentProps<TValue, TName> & {
    accessibilityLayer?: boolean;
    active?: boolean | undefined;
    includeHidden?: boolean | undefined;
    allowEscapeViewBox?: AllowInDimension;
    animationDuration?: AnimationDuration;
    animationEasing?: AnimationTiming;
    content?: ContentType<TValue, TName>;
    coordinate?: Partial<Coordinate>;
    cursor?: boolean | ReactElement | SVGProps<SVGElement>;
    filterNull?: boolean;
    defaultIndex?: number;
    isAnimationActive?: boolean;
    offset?: number;
    payloadUniqBy?: UniqueOption<Payload<TValue, TName>>;
    position?: Partial<Coordinate>;
    reverseDirection?: AllowInDimension;
    shared?: boolean;
    trigger?: 'hover' | 'click';
    useTranslate3d?: boolean;
    viewBox?: CartesianViewBox;
    wrapperStyle?: CSSProperties;
};
export declare class Tooltip<TValue extends ValueType, TName extends NameType> extends PureComponent<TooltipProps<TValue, TName>> {
    static displayName: string;
    static defaultProps: {
        accessibilityLayer: boolean;
        allowEscapeViewBox: {
            x: boolean;
            y: boolean;
        };
        animationDuration: number;
        animationEasing: string;
        contentStyle: {};
        coordinate: {
            x: number;
            y: number;
        };
        cursor: boolean;
        cursorStyle: {};
        filterNull: boolean;
        isAnimationActive: boolean;
        itemStyle: {};
        labelStyle: {};
        offset: number;
        reverseDirection: {
            x: boolean;
            y: boolean;
        };
        separator: string;
        trigger: string;
        useTranslate3d: boolean;
        viewBox: {
            x: number;
            y: number;
            height: number;
            width: number;
        };
        wrapperStyle: {};
    };
    render(): React.JSX.Element;
}
