import EventEmitter from 'eventemitter3';
import { CategoricalChartState } from '../chart/types';
declare const eventCenter: EventEmitter<EventTypes>;
export { eventCenter };
export declare const SYNC_EVENT = "recharts.syncMouseEvents";
interface EventTypes {
    [SYNC_EVENT](syncId: number | string, data: CategoricalChartState, emitter: Symbol): void;
}
