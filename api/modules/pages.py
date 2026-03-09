"""Page Routes Handler"""
from flask import render_template


class PageAPI:
    """Handle page rendering for frontend routes"""
    
    @staticmethod
    def index():
        """Main index page"""
        return render_template("index.html")
    
    @staticmethod
    def bom():
        """BOM page"""
        return render_template("bom.html")
    
    @staticmethod
    def category(category_name):
        """Category page"""
        return render_template("category.html", category_name=category_name)
    
    @staticmethod
    def brand():
        """Brand page"""
        return render_template("brand.html")
    
    @staticmethod
    def contact():
        """Contact page"""
        return render_template("contact.html")
    
    @staticmethod
    def faq():
        """FAQ page"""
        return render_template("faq.html")
    
    @staticmethod
    def product(partnumber):
        """Product detail page"""
        return render_template("product.html", partnumber=partnumber)
    
    @staticmethod
    def upload():
        """Upload page"""
        return render_template("upload.html")
    
    @staticmethod
    def introduction():
        """Introduction page"""
        return render_template("introduction.html")
