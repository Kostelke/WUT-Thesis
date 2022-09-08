import { Component, OnInit } from '@angular/core';
import { ClientApi } from "../api/client-api";
import { from } from "rxjs";
import { first } from "rxjs/operators";
import { DataHandlingService } from "../api/data-handling.service";
import { FormBuilder, FormGroup, Validators } from "@angular/forms";

export interface Node {
  "nodeName": string,
  "demand": number[],
  "index": number,
  "plants": [],
}

export interface Edge {
  "name": string,
  "capacity": number,
  "admitance": number,
  "voltageA": number,
  "voltageB": number,
  "nodeA": string,
  "nodeB": string,
}

export interface Plant {
  "sourceNode": string
  "plantName": string,
  "blockName": string,
  "Pmin": number,
  "Pmax": number,
  "ramp"?: number,

}

@Component({
  selector: 'app-topbar',
  templateUrl: './topbar.component.html',
  styleUrls: ['./topbar.component.scss']
})
export class TopbarComponent implements OnInit {

  private nodeJSON: Node[] = [];
  private edgeJSON: Edge[] = [];
  private plantJSON: Plant[] = [];
  private config = {
    mode: "simple",
    enforceStrict: true,
    timeMax: 1,
  }

  public _formGroup: FormGroup;
  public nodeLoaded = false;
  public edgeLoaded = false;
  public plantLoaded = false;
  public enable = false;
  public resultButtonText = "Send Data"

  constructor(
    private readonly _dataHandlingService: DataHandlingService,
    private readonly _formBuilder: FormBuilder,
  ) {
  }

  ngOnInit(): void {
    this._dataHandlingService._loadingObservable.subscribe(x => {
      x ? this.resultButtonText = "Loading..." : this.resultButtonText = "Send Data";
    });
    this._formGroup = this._formBuilder.group({
      mode: "Simple",
      enforce: ["False"],
      length: [null, Validators.required]
    });
    this._formGroup.valueChanges.subscribe(x => {
        this.config["mode"] = x.mode;
        this.config["timeMax"] = x.length;
        this.config["enforceStrict"] = x.enforce === "True";
        if (this.nodeLoaded && this.edgeLoaded && this.plantLoaded && this._formGroup.valid) {
          this.enable = true;
      }
      }
    )
  }


  public onNodeSelected($event: Event) {
    const event = $event.target as HTMLInputElement;
    if (event.files![0]) {
      this.saveNode(event.files!);
    }
  }

  public onEdgeSelected($event: Event) {
    const event = $event.target as HTMLInputElement;
    if (event.files![0]) {
      this.saveEdge(event.files!);
    }
  }

  public onPlantSelected($event: Event) {
    const event = $event.target as HTMLInputElement;
    if (event.files![0]) {
      this.savePlant(event.files!);
    }
  }

  public saveEdge(files: FileList) {
    if (files.length > 1) {
      console.log('Too many files, please upload only one file!');
    } else {
      const fromPromise$ = from(files[0].text());
      let arr: string[] = [];

      fromPromise$.pipe(first()).subscribe(
        next => {
          arr = next.split("\n");
          const edgeList: Edge[] = [];
          let index = 0;
          arr.forEach((x) => {
            const line = x.split(",");
            const edgeToPush: Edge = {
              "name": line[0] + line[1],
              "capacity": +line[2],
              "admitance": +line[3],
              "voltageA": +line[4],
              "voltageB": +line[5],
              "nodeA": line[0],
              "nodeB": line[1],
            };
            edgeList.push(edgeToPush);
            index = index + 1;
          });
          this.edgeJSON = edgeList;
        },
      );
    }
    this.edgeLoaded = true;
    if (this.nodeLoaded && this.edgeLoaded && this.plantLoaded && this._formGroup.valid) {
      this.enable = true;
    }
  }

  public savePlant(files: FileList) {
    if (files.length > 1) {
      console.log('Too many files, please upload only one file!');
    } else {
      const fromPromise$ = from(files[0].text());
      let arr: string[] = [];
      fromPromise$.pipe(first()).subscribe(
        next => {
          arr = next.split("\n");
          const plantList: Plant[] = [];
          let index = 0;
          arr.forEach((x) => {
            const line = x.split(",");
            const plantToPush: Plant = {
              "sourceNode": line[0],
              "plantName": line[1],
              "blockName": line[2],
              "Pmin": +line[3],
              "Pmax": +line[4],
            };
            if (line[6]) {
              plantToPush["ramp"] = +line[6];
            }
            plantList.push(plantToPush);
            index = index + 1;
          });
          this.plantJSON = plantList;
        },
      );
    }
    this.plantLoaded = true;
    if (this.nodeLoaded && this.edgeLoaded && this.plantLoaded && this._formGroup.valid) {
      this.enable = true;
    }

  }

  public saveNode(files: FileList) {
    if (files.length > 1) {
      console.log('Too many files, please upload only one file!');
    } else {
      const fromPromise$ = from(files[0].text());
      let arr: string[] = [];

      fromPromise$.pipe(first()).subscribe(
        next => {
          arr = next.split("\n");
          const nodeList: Node[] = [];
          let index = 0;
          arr.forEach((x) => {
            const line = x.split(",");
            const nodeToPush: Node = {
              "nodeName": line[0],
              "index": index,
              "plants": [],
              "demand": [],
            };
            const dem = line[1].split(" ");
            let demandArray: number[] = [];
            dem.forEach(x =>
            demandArray.push(+x))
            nodeToPush["demand"] = demandArray;
            nodeList.push(nodeToPush);
            index = index + 1;
          });
          this.nodeJSON = nodeList;
        },
      );
    }
    this.nodeLoaded = true;
    if (this.nodeLoaded && this.edgeLoaded && this.plantLoaded && this._formGroup.valid) {
      this.enable = true;
    }
  }

  public send() {
    let postNodeJSON = [];
    this.nodeJSON.forEach(x =>
      postNodeJSON.push(x),
    );
    let postEdgeJSON = [];
    this.edgeJSON.forEach(x =>
      postEdgeJSON.push(x),
    );
    let postPlantJSON = [];
    this.plantJSON.forEach(x => {
        postPlantJSON.push(x)
      }
    );
    this._dataHandlingService.postFiles(JSON.stringify(postNodeJSON), JSON.stringify(postEdgeJSON), JSON.stringify(postPlantJSON), JSON.stringify(this.config));
  }
}

