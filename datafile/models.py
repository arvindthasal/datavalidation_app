from django.db import models, connection
from collections import namedtuple


class Exceldata(models.Model):
    country = models.CharField(max_length=255)
    bevarage_type = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    total_volume = models.IntegerField()
    total_value = models.FloatField()
    unit_price = models.FloatField()

    # function to get all rows of uploaded excel file 
    def get_excelvalidate_data():

        cursor = connection.cursor()
        cursor.execute("SELECT t.country as country ,t.bevarage_type,t.category,t.total_volume,t.total_value,t.unit_price,c.total_vol,(cast(t.total_volume as decimal)*cast(t.unit_price as decimal))=cast(t.total_value as decimal) as check_over_price ,(t.total_volume/cast(c.total_vol as decimal)) as percentage FROM datafile_exceldata t INNER JOIN (SELECT country,SUM(total_volume) AS total_vol FROM datafile_exceldata GROUP BY country) c ON c.country=t.country")
        desc = cursor.description
        nt_result = namedtuple('Result', [col[0] for col in desc])
        return [nt_result(*row) for row in cursor.fetchall()]

    
