const renderChart=(data,labels) => {
    const ctx = document.getElementById('myChart');

    new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: labels,
        data: data,
        datasets: [{
            label: 'Expenses in the last 6 months',
            data: data,
            borderWidth: 1,
            backgroundColor: [
                'rgb(255, 99, 132)',
                'rgb(54, 162, 235)',
                'rgb(255, 205, 86)'
              ],
            hoverOffset: 4
            }]
    },
    options: {
        title:{
            display: true,
            text: 'Expenses per category',
            },
        },
    });
};

const getChartData=() => {
    console.log("fetching");

    fetch('expense_summary')
    .then((res) => res.json())
    .then((results) => {
        console.log("results", results);
        const category_data=results.expense_category_data;
        const [labels,data]= [
            Object.keys(category_data), 
            Object.values(category_data),
        ];

        renderChart(data,labels);
    });
}
window.onload=getChartData;