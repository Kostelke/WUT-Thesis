
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { map, switchMap, tap } from 'rxjs/operators';
import { Injectable } from '@angular/core';
import { Observable } from "rxjs";

const BASE_URL = 'http://localhost:5000/api';

interface answer  { test: string }

export interface graphNode {
  group: string,
  data: {
    id: string,
    demand: number,
    }
  }
export interface graphEdge {
  group: string,
  data: {
    source: string,
    target: string,
    value: number,
    percentage: number
  }
}

export interface graphPlants {
  group: string,
  data: {
    id: string,
    parent: string,
    value: number,
    isWorking: number
  }
}

export interface ResultJSON {
  nodes: JSON[],
  edges: JSON[],
  plants: JSON[]
}
export interface TimePeriodResult {
  results: ResultJSON []
}

@Injectable({
  providedIn: 'root',
})
export class ClientApi  {

  constructor(
    private readonly _http: HttpClient,
  ) {
  }

  public getJson(): Observable<answer>{
    const url = BASE_URL + '/nodes-results';
    const options = {
      responseType: 'json' as 'json',
      contentType: 'application/json',
    };

    return this._http.get(url).pipe(
      map(result => result as answer),
    );
  }

  public postNodesJson(inputJSON: string ): Observable<answer> {
    const url = BASE_URL + '/post-nodes';
    let headers = new HttpHeaders();
    headers = headers.set('Content-Type', 'application/json; charset=utf-8');
    const options = {
      responseType: 'json' as 'json',
      headers: headers,
    };
    return this._http.post(url, inputJSON, options).pipe(
      map(result => result as answer),
    );
  }
  public postEdgesJson(inputJSON: string ): Observable<answer> {
    const url = BASE_URL + '/post-edges';
    let headers = new HttpHeaders();
    headers = headers.set('Content-Type', 'application/json; charset=utf-8');
    const options = {
      responseType: 'json' as 'json',
      headers: headers,
    };
    return this._http.post(url, inputJSON, options).pipe(
      map(result => result as answer),
    );
  }
  public postPlantsJson(inputJSON: string ): Observable<answer> {
    const url = BASE_URL + '/post-plants';
    let headers = new HttpHeaders();
    headers = headers.set('Content-Type', 'application/json; charset=utf-8');
    const options = {
      responseType: 'json' as 'json',
      headers: headers,
    };
    return this._http.post(url, inputJSON, options).pipe(
      map(result => result as answer),
    );
  }

  public postConfig(inputJSON: string): Observable<answer> {
    const url = BASE_URL + '/post-config';
    let headers = new HttpHeaders();
    headers = headers.set('Content-Type', 'application/json; charset=utf-8');
    const options = {
      responseType: 'json' as 'json',
      headers: headers,
    };
    return this._http.post(url, inputJSON, options).pipe(
      map(result => result as answer),
    );
  }

  public getResults(): Observable<ResultJSON> {
    const url = BASE_URL + '/get-results';
    let headers = new HttpHeaders();
    headers = headers.set('Content-Type', 'application/json; charset=utf-8');
    const options = {
      responseType: 'json' as 'json',
      headers: headers,
    };
    return this._http.get(url,options).pipe(
      map(result => result as ResultJSON),
    );
  }

  public getNext(): Observable<ResultJSON> {
    const url = BASE_URL + '/next';
    let headers = new HttpHeaders();
    headers = headers.set('Content-Type', 'application/json; charset=utf-8');
    const options = {
      responseType: 'json' as 'json',
      headers: headers,
    };
    return this._http.get(url,options).pipe(
      map(result => result as ResultJSON),
    );
  }
  public getPrev(): Observable<ResultJSON> {
    const url = BASE_URL + '/prev';
    let headers = new HttpHeaders();
    headers = headers.set('Content-Type', 'application/json; charset=utf-8');
    const options = {
      responseType: 'json' as 'json',
      headers: headers,
    };
    return this._http.get(url,options).pipe(
      map(result => result as ResultJSON),
    );
  }
}
