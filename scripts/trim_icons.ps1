<#
.SYNOPSIS
  Makes the background of figures/controller_icons/*.png transparent and trims
  the surrounding margin.

.DESCRIPTION
  The source icons ship with an opaque white margin around the drawn tile.  That
  margin is invisible on a white slide but shows as a white halo -- and hides
  arrowheads -- once the figure places the icons on filled region cards.

  Background is found by flood filling inward from the image border, so only
  white that is connected to the edge is cleared; the white *inside* the tile is
  kept.  The result is cropped to the remaining ink and padded back to a square
  so the build script can place it as an exact tile.

  Idempotent: re-running on an already trimmed icon is a no-op.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts/trim_icons.ps1
#>

[CmdletBinding()]
param(
  [string]$IconDir = (Join-Path $PSScriptRoot "..\figures\controller_icons"),
  [int]$WhiteThreshold = 244
)

Add-Type -AssemblyName System.Drawing

Add-Type -TypeDefinition @"
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;

public static class IconTrimmer
{
    public static string Trim(string path, int whiteThreshold)
    {
        int w, h;
        byte[] buf;
        using (Bitmap src = new Bitmap(path))
        {
            w = src.Width;
            h = src.Height;
            using (Bitmap rgba = new Bitmap(w, h, PixelFormat.Format32bppArgb))
            {
                using (Graphics g = Graphics.FromImage(rgba)) { g.DrawImage(src, 0, 0, w, h); }
                BitmapData bd = rgba.LockBits(new Rectangle(0, 0, w, h),
                    ImageLockMode.ReadOnly, PixelFormat.Format32bppArgb);
                buf = new byte[bd.Stride * h];
                Marshal.Copy(bd.Scan0, buf, 0, buf.Length);
                rgba.UnlockBits(bd);
            }
        }

        // Flood fill the background inward from every border pixel.
        bool[] bg = new bool[w * h];
        bool[] seen = new bool[w * h];
        System.Collections.Generic.Stack<int> stack = new System.Collections.Generic.Stack<int>();
        for (int x = 0; x < w; x++)
        {
            if (!seen[x]) { seen[x] = true; stack.Push(x); }
            int bi = (h - 1) * w + x;
            if (!seen[bi]) { seen[bi] = true; stack.Push(bi); }
        }
        for (int y = 0; y < h; y++)
        {
            int li = y * w, ri = y * w + (w - 1);
            if (!seen[li]) { seen[li] = true; stack.Push(li); }
            if (!seen[ri]) { seen[ri] = true; stack.Push(ri); }
        }

        while (stack.Count > 0)
        {
            int idx = stack.Pop();
            int o = idx * 4;
            byte b = buf[o], g2 = buf[o + 1], r = buf[o + 2], a = buf[o + 3];
            bool isBg = a < 16 || (r >= whiteThreshold && g2 >= whiteThreshold && b >= whiteThreshold);
            if (!isBg) continue;
            bg[idx] = true;
            int px = idx % w, py = idx / w;
            if (px > 0 && !seen[idx - 1]) { seen[idx - 1] = true; stack.Push(idx - 1); }
            if (px < w - 1 && !seen[idx + 1]) { seen[idx + 1] = true; stack.Push(idx + 1); }
            if (py > 0 && !seen[idx - w]) { seen[idx - w] = true; stack.Push(idx - w); }
            if (py < h - 1 && !seen[idx + w]) { seen[idx + w] = true; stack.Push(idx + w); }
        }

        // Bound by row/column ink counts, so a stray speck in the source margin
        // cannot drag the crop box outwards.
        int[] colInk = new int[w];
        int[] rowInk = new int[h];
        for (int i = 0; i < w * h; i++)
        {
            if (bg[i]) { buf[i * 4 + 3] = 0; continue; }
            colInk[i % w]++;
            rowInk[i / w]++;
        }
        const int MIN_INK = 3;
        int minX = -1, maxX = -1, minY = -1, maxY = -1;
        for (int x = 0; x < w; x++) { if (colInk[x] >= MIN_INK) { if (minX < 0) minX = x; maxX = x; } }
        for (int y = 0; y < h; y++) { if (rowInk[y] >= MIN_INK) { if (minY < 0) minY = y; maxY = y; } }
        if (maxX < 0 || maxY < 0) return "empty";

        int cw = maxX - minX + 1, ch = maxY - minY + 1;
        int side = Math.Max(cw, ch);
        int offX = (side - cw) / 2, offY = (side - ch) / 2;

        using (Bitmap outBmp = new Bitmap(side, side, PixelFormat.Format32bppArgb))
        {
            BitmapData od = outBmp.LockBits(new Rectangle(0, 0, side, side),
                ImageLockMode.WriteOnly, PixelFormat.Format32bppArgb);
            byte[] obuf = new byte[od.Stride * side];
            for (int y = 0; y < ch; y++)
            {
                for (int x = 0; x < cw; x++)
                {
                    int s = ((minY + y) * w + (minX + x)) * 4;
                    int d = (offY + y) * od.Stride + (offX + x) * 4;
                    obuf[d] = buf[s]; obuf[d + 1] = buf[s + 1];
                    obuf[d + 2] = buf[s + 2]; obuf[d + 3] = buf[s + 3];
                }
            }
            Marshal.Copy(obuf, 0, od.Scan0, obuf.Length);
            outBmp.UnlockBits(od);
            outBmp.Save(path + ".tmp", ImageFormat.Png);
        }
        return string.Format("{0}x{1} -> {2}x{2}", w, h, side);
    }
}
"@ -ReferencedAssemblies System.Drawing

$dir = (Resolve-Path $IconDir).Path
foreach ($file in (Get-ChildItem $dir -Filter *.png | Sort-Object Name)) {
  $result = [IconTrimmer]::Trim($file.FullName, $WhiteThreshold)
  Move-Item -Force ($file.FullName + ".tmp") $file.FullName
  "{0,-26} {1}" -f $file.Name, $result
}
