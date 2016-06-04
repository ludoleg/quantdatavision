class testscipy(webapp2.RequestHandler):
    def get(self):
        # Parse command-line arguments
        # parser = argparse.ArgumentParser(usage=__doc__)
        # parser.add_argument("--order", type=int, default=3, help="order of Bessel function")
        # parser.add_argument("--output", default="plot.png", help="output image file")
        # args = parser.parse_args()

        # Compute maximum
        
        f = lambda x: -special.jv(3, x)
        sol = optimize.minimize(f, 1.0)

        # Plot
        x = np.linspace(0, 10, 5000)
        # plt.plot(x, special.jv(args.order, x), '-', sol.x, -sol.fun, 'o')

        plt.plot(x, special.jv(3, x), '-', sol.x, -sol.fun, 'o')
        rv_plot = StringIO.StringIO()
        # Produce output
        # plt.savefig(args.output, dpi=96)
        plt.title("SciPy PNG")
        plt.savefig(rv_plot, dpi=96, format="png")
        plt.clf()
        png_img = """<img src="data:image/png;base64,%s"/>""" % rv_plot.getvalue().encode("base64").strip()
        self.response.write("""<html><head/><body>""")
        self.response.write("Scipy")
        self.response.write(png_img)
        self.response.write("""</body> </html>""")
