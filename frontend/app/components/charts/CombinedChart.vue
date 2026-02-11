<template>
  <VChart :option="option" autoresize />
</template>

<script setup lang="ts">
import { provide } from "vue";

// provide init-options
const renderer = ref<"svg" | "canvas">("svg");
const initOptions = computed(() => ({
  height: 600,
  renderer: renderer.value,
}));
provide(INIT_OPTIONS_KEY, initOptions);

const source=GetMockupData()
// Compute base to stack
var base = -source.reduce(function (min, val) {
    return Math.floor(Math.min(min, val.Min));
  }, Infinity);

function ShortDate(date){
    return [date.getMonth() + 1, date.getDate(),date.getMonth() + 1,date.getYear()].join('/')
}
const option = ref<ECOption>({
  dataset: {
    dimensions: ["date", "ITN","StdDev"],
    source: source,
  },
   tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
          animation: false,
          label: {
            backgroundColor: '#ccc',
            borderColor: '#aaa',
            borderWidth: 1,
            shadowBlur: 0,
            shadowOffsetX: 0,
            shadowOffsetY: 0,
            color: '#222'
          }
        },
        formatter: function (params) {
            console.log("Params",params)
            const Idx  = params[0].dataIndex
          return (

            ShortDate(source[Idx].date) +
            '<br />' +
            ((source[Idx].ITN ) ).toFixed(2) +'°C'
          );
        }
      },
  xAxis: {
        type: 'category',
        data: source.map(function (item) {
          return item.date;
        }),
        axisLabel: {
          formatter: function (value, idx) {
            var date = new Date(value);
            return ShortDate(date);
          }
        },
        boundaryGap: false
      },
   yAxis: {
        axisLabel: {
          formatter: function (val) {
            return (val - base) +' °C';
          }
        },
        axisPointer: {
          label: {
            formatter: function (params) {
              return ((params.value - base)).toFixed(2) + '°c';
            }
          }
        },
        splitNumber: 3
      },
  labels: source.map((item)=>{ return item.date}),
  series:[
        { 
          name: 'ITN',
          type: 'line',
          data: source.map(function (item) {
            return base + item.ITN
          }),
          lineStyle: {
            color: '#130707'
          },
          showSymbol: false
        },
        { 
          name: 'Delta',
          type: 'line',
          data: source.map(function (item) {
            return base + item.ITN+item.Delta
          }),
          lineStyle: {
            color: '#2d3ed3',
            width:0.75

          },
          showSymbol: false
        },
        { 
          name: 'Min',
          type: 'line',
          data: source.map(function (item) {
            return base +item.Min
          }),
          stack:'MinMax',
          lineStyle: {
            opacity:0,            
          },
          showSymbol: false
        },
        ,
        { 
          name: 'Max',
          type: 'line',
          data: source.map(function (item) {
            return item.Max-item.Min
          }),
          stack:'MinMax',
          lineStyle: {
            opacity:0,            
          },
          areaStyle:{
            color:'#777777',
          },
          showSymbol: false
        },
        { 
          name: 'Ldev',
          type: 'line',
          data: source.map(function (item) {
            return base +item.ITN - item.StdDev
          }),
          stack:'bands',
          lineStyle: {
            opacity:0,            
          },
          showSymbol: false
        },
        
        { 
          name: 'UDev',
          type: 'line',
          data: source.map(function (item) {
            return 2* item.StdDev
          }),
          stack:'bands',
          lineStyle: {
            opacity:0,            
          },
          areaStyle: {
            color:'#cccccc',
          },
          showSymbol: false
        },
        
        ]
})
  
// function LayoutChartLines(data)
// {
//     return {
//         labels: data.map(item => item.date),
//         datasets: [
//             {
//                 label: 'ITN',
//                 data: data.map(item => item.ITN),
//                 borderColor: 'rgba(75, 192, 192, 1)',
//                 fill: false, // No fill under the line
//                 pointRadius: 0 // No points
//             },
//             {
//                 label: 'iTN+sd',
//                 data: data.map(item => item.iTN+item.St),
//                 borderColor: 'rgba(255, 99, 132, 1)',
//                 fill: false,
//                 pointRadius: 0 // No points
//             },
//             {
//                 label: 'Line 3',
//                 data: data.map(item => item.line3),
//                 borderColor: 'rgba(255, 206, 86, 1)',
//                 fill: false,
//                 pointRadius: 0 // No points
//             }
//         ]
//     };
// }


//Generate random temp
function GetMockupData()
{
    const RetArray=[]
    let CurTemp=5
    let CurDate=  new Date('2025-01-01')
    let Dt = 0
    for (let i=0; i<365; i++)
    {
        //CurTemp+=Math.random()*5-2.5
        CurTemp= 10*Math.sin((i-100)/180*3.141592654)+6+Math.random()*3-1.5
        const Std = 5*Math.random()
         Dt = Math.sin((i-100)/18*3.141592654)*4+Math.random()*3-1.5
        RetArray.push(    { date: CurDate, ITN: CurTemp,Delta:Dt, StdDev:Std , Min: CurTemp-Std-Std*Math.random(), Max: CurTemp+Std+Std*Math.random() })
        CurDate = new Date(CurDate.getTime()+24*3600*1000)
        
    }

    return RetArray
}
</script>