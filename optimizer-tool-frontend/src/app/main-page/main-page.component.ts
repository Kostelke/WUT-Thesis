import { Component, OnInit } from '@angular/core';
import * as cytoscape from 'cytoscape';
import coseBilkent from 'cytoscape-cose-bilkent';
import { edgeLoadColors } from "./styles";
import { Subscription } from "rxjs";
import { DataHandlingService } from "../api/data-handling.service";

cytoscape.use(coseBilkent);


@Component({
  selector: 'app-main-page',
  templateUrl: './main-page.component.html',
  styleUrls: ['./main-page.component.scss']
})
export class MainPageComponent implements OnInit {
  private _subscription: Subscription = new Subscription();
  private nodes = [];
  private edges = [];
  private plants = [];
  public index = 0;
  private cy = cytoscape();
  private elems;
  private nodeCollection;
  private edgeCollection;
  private plantCollection;

  public disablePageButtons = true;

  constructor(
    private readonly _dataHandlingService: DataHandlingService,
  ) {
  }

  ngOnInit(): void {

    this.cy = cytoscape({
      container: document.getElementById('cy'),
      layout: {
        name: "cose-bilkent",
      },
      style: [
        {
          selector: 'node',
          style: {
            'label': 'data(id)',
            'font-size': '6px',
            'width': '4px',
            'height': '4px',
            // 'background-color': "rgb(1,1,1)",
          }
        },
        {
          selector: ':child',
          style: {
            'label': 'data(id)',
            'font-size': '2px',
            'width': '2px',
            'height': '2px',
            'background-color': "rgb(1,1,1)",
          }
        },
        {
          selector: 'edge',
          style: {
            'label': 'data(value)',
            'font-size': '4px',
            'width': '1px',
          }
        },
        {
          selector: ':child[isWorking = 0]',
          style: {
            'label': 'data(id)',
            'font-size': '2px',
            'width': '2px',
            'height': '2px',
            'background-color': "rgb(255,0,0)",
          },
        },
        {
          selector: ':child[isWorking = 1]',
          style: {
            'label': 'data(id)',
            'font-size': '2px',
            'width': '2px',
            'height': '2px',
            'background-color': "rgb(0,255,0)",
          },
        },

        ...edgeLoadColors
      ]
    });

    cytoscape.use(coseBilkent);
    this.cy.layout(
      {
        name: 'cose-bilkent',
      }
    ).run();

    this._subscription.add(this._dataHandlingService._resultJSONObservable.subscribe(result => {
      if (result !== undefined) {
        console.log(result);
        if (this.nodes.length === 0) {
          this.nodes = result.nodes;
          this.edges = result.edges;
          this.plants = result.plants;
          this.nodeCollection = this.cy.add(this.nodes);
          this.plantCollection = this.cy.add(this.plants);
          this.edgeCollection = this.cy.add(this.edges);
          this.cy.layout(
            {
              name: 'cose-bilkent',
            }
          ).run();
        } else {
          this.nodes = result.nodes;
          this.edges = result.edges;
          this.plants = result.plants;
          this.updateGraph()
        }
      }
    }));
    this._subscription.add(this._dataHandlingService._loadingObservable.subscribe(x => {
      this.disablePageButtons = x;
    }))

    this.cy.on('tap', 'node', function(evt){
      let node = evt.target;
      let message = "";

      console.log(node.data("demand"));
    });
  }


  private updateGraph() {
    let index = 0;
    this.nodeCollection.forEach(x => {
      x.data('demand', this.nodes[index].data.demand);
      index++;
    })
    index = 0;
    this.edgeCollection.forEach(x => {
      x.data('percentage', this.edges[index].data.percentage);
      x.data('value', this.edges[index].data.value);
      index++;
    })
    index = 0;
    this.plantCollection.forEach(x => {
      x.data('value', this.plants[index].data.value);
      x.data('isWorking', this.plants[index].data.isWorking);
      index++;
    })
  }

  public onNext() {
    this.index++;
    this._dataHandlingService.nextPeriod();
  }

  public onPrev() {
    this.index--;
    this._dataHandlingService.prevPeriod();
  }
}
