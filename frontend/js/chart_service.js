// Chart.js Service for VietJourney AI Analytics
window.ChartService = {
  revenueChartInstance: null,
  occupancyChartInstance: null,

  isDarkMode: function() {
    return document.documentElement.classList.contains('dark');
  },

  initRevenueChart: function(canvasId, topToursData) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    if (this.revenueChartInstance) {
      this.revenueChartInstance.destroy();
    }

    const isDark = this.isDarkMode();
    const textColor = isDark ? '#94a3b8' : '#64748b';
    const gridColor = isDark ? 'rgba(148, 163, 184, 0.12)' : 'rgba(0, 0, 0, 0.06)';

    const hasData = Array.isArray(topToursData) && topToursData.length > 0;
    const labels = hasData 
      ? topToursData.map(t => t.code || t.title) 
      : ['Chưa có dữ liệu'];
      
    const dataValues = hasData 
      ? topToursData.map(t => (t.revenue || 0) / 1000000) 
      : [0];

    const ctx = canvas.getContext('2d');
    this.revenueChartInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Doanh thu (Triệu VNĐ)',
          data: dataValues,
          backgroundColor: hasData ? 'rgba(2, 132, 199, 0.85)' : 'rgba(148, 163, 184, 0.3)',
          borderColor: hasData ? 'rgb(2, 132, 199)' : 'rgba(148, 163, 184, 0.5)',
          borderWidth: 1.5,
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: function(context) {
                return (context.parsed.y || 0).toLocaleString('vi-VN') + ' Triệu VNĐ';
              }
            }
          }
        },
        scales: {
          x: {
            ticks: { color: textColor, font: { size: 11 } },
            grid: { display: false }
          },
          y: {
            beginAtZero: true,
            ticks: {
              color: textColor,
              font: { size: 11 },
              callback: function(val) { return val + ' tr'; }
            },
            grid: { color: gridColor }
          }
        }
      }
    });
  },

  initOccupancyChart: function(canvasId, avgRate) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    if (this.occupancyChartInstance) {
      this.occupancyChartInstance.destroy();
    }

    const isDark = this.isDarkMode();
    const textColor = isDark ? '#cbd5e1' : '#475569';
    const emptyBg = isDark ? '#1e293b' : '#e2e8f0';

    const rate = Math.min(100, Math.max(0, avgRate ?? 0));
    const remaining = 100 - rate;

    const ctx = canvas.getContext('2d');
    this.occupancyChartInstance = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Đã đặt chỗ (%)', 'Còn trống (%)'],
        datasets: [{
          data: [rate, remaining],
          backgroundColor: ['#0284c7', emptyBg],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '72%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: textColor,
              font: { size: 11, weight: '600' },
              padding: 16
            }
          }
        }
      }
    });
  }
};
