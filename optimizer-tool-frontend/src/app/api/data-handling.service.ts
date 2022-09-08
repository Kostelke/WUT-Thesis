import { Injectable } from '@angular/core';
import { ClientApi, ResultJSON, TimePeriodResult } from "./client-api";
import { BehaviorSubject, merge, Observable } from "rxjs";
import { first } from "rxjs/operators";



@Injectable({
  providedIn: 'root'
})
export class DataHandlingService {
  private currentIndex = 0;
  private readonly _resultJSONSubject: BehaviorSubject<ResultJSON> = new BehaviorSubject<ResultJSON>(undefined);
  public readonly _resultJSONObservable: Observable<ResultJSON> = this._resultJSONSubject.asObservable();


  private readonly _loadingSubject: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);
  public readonly _loadingObservable: Observable<boolean> = this._loadingSubject.asObservable();
  constructor(
    private readonly _clientAPI: ClientApi,
    ) { }

  public postFiles(nodes: string, edges: string, plants: string, config: string){
    this._loadingSubject.next(true);
    this._clientAPI.postConfig(config).pipe(first()).subscribe(x => {
      this._clientAPI.postEdgesJson(edges).pipe(first()).subscribe();
      this._clientAPI.postNodesJson(nodes).pipe(first()).subscribe(x => {
        this._clientAPI.postPlantsJson(plants).pipe(first()).subscribe( x => {
          this._clientAPI.getResults().subscribe(x => {
            this.currentIndex = 0;
            this._resultJSONSubject.next(x);
            this._loadingSubject.next(false);
          });
        });
      });
    });
  }

  public nextPeriod(){
    this._loadingSubject.next(true);
      this.currentIndex += 1;
      this._clientAPI.getNext().pipe(first()).subscribe(x => {
        this._resultJSONSubject.next(x);
        this._loadingSubject.next(false);
      })
  }

  public prevPeriod(){
    this._loadingSubject.next(true);
    this.currentIndex -= 1;
      this._clientAPI.getPrev().pipe(first()).subscribe(x => {
        this._resultJSONSubject.next(x);
        this._loadingSubject.next(false);
      })
  }
}
