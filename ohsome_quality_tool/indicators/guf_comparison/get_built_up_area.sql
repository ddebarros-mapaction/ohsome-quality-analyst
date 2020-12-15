-- This SQL Query is meant to be used with psycopg2.
SELECT
    SUM(ST_Area ((pixel_as_polygon).geom::geography))
FROM (
    SELECT
        -- ST_PixelAsPolygons will exclude pixel with nodata values
        ST_PixelAsPolygons (ST_Clip (rast, ST_GeomFromGeoJSON (%s))) AS pixel_as_polygon
    FROM
        guf04_daressalaam
    WHERE
        ST_Intersects (rast, ST_GeomFromGeoJSON (%s))
        -- Avoid following ERROR of rt_raster_from_two_rasters during ST_Clip:
        -- The two rasters provided do not have the same alignment
        AND ST_BandIsNoData (rast) = FALSE) AS foo;
